"""
Streaming Graph Service

Service layer managing streaming LangGraph sessions for emergency dispatch.
Handles session creation, transcript processing, and response formatting.

This service integrates the streaming workflow with the WebSocket layer,
providing a clean interface for real-time audio processing.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from uuid import uuid4

from graph.streaming_state import (
    StreamingEmergencyState,
    create_streaming_initial_state,
    update_streaming_state_with_transcript,
)
from graph.streaming_workflow import invoke_streaming_graph, get_streaming_graph

logger = logging.getLogger(__name__)


class StreamingGraphService:
    """Service for managing streaming LangGraph sessions.

    This service provides:
    - Session creation and management
    - Transcript chunk processing through the streaming graph
    - Response formatting for WebSocket communication
    - Session state tracking
    """

    def __init__(
        self,
        confidence_threshold: float = 0.75,
        evaluation_window_seconds: float = 10.0
    ):
        """Initialize the streaming graph service.

        Args:
            confidence_threshold: Confidence threshold for evaluation (default: 0.75)
            evaluation_window_seconds: Maximum evaluation window in seconds (default: 10.0)
        """
        self.confidence_threshold = confidence_threshold
        self.evaluation_window_seconds = evaluation_window_seconds
        self._active_sessions: Dict[str, StreamingEmergencyState] = {}

        logger.info(
            f"StreamingGraphService initialized: "
            f"threshold={confidence_threshold}, window={evaluation_window_seconds}s"
        )

    def create_session(self, session_id: Optional[str] = None) -> StreamingEmergencyState:
        """Create a new streaming session.

        Args:
            session_id: Optional session ID (generated if not provided)

        Returns:
            Initial StreamingEmergencyState for the session
        """
        if session_id is None:
            session_id = f"stream-{uuid4().hex[:12]}"

        state = create_streaming_initial_state(
            session_id=session_id,
            confidence_threshold=self.confidence_threshold,
            evaluation_window_seconds=self.evaluation_window_seconds
        )

        # Track active session
        self._active_sessions[session_id] = state

        logger.info(f"[Session {session_id}] Created new streaming session")
        return state

    def process_transcript_chunk(
        self,
        state: StreamingEmergencyState,
        transcript_chunk: str,
        detected_language: str = None
    ) -> Tuple[StreamingEmergencyState, Dict[str, Any]]:
        """Process a new transcript chunk through the streaming graph.

        This method:
        1. Updates the state with the new transcript chunk
        2. Invokes the streaming graph for classification
        3. Formats the response for WebSocket communication

        Args:
            state: Current streaming session state
            transcript_chunk: New transcript text to process
            detected_language: Language detected by STT (optional)

        Returns:
            Tuple of (updated_state, websocket_response)
        """
        session_id = state.get("session_id", "unknown")
        chunk_num = state.get("chunk_count", 0) + 1
        chunk_received_at = datetime.utcnow().isoformat()

        logger.info(f"[Session {session_id}] Processing chunk #{chunk_num}: {len(transcript_chunk)} chars")

        # Update state with new transcript
        updated_state = update_streaming_state_with_transcript(
            state=state,
            new_transcript_chunk=transcript_chunk,
            detected_language=detected_language,
            chunk_received_at=chunk_received_at
        )

        # Update metrics with graph start time
        metrics = dict(updated_state.get("processing_metrics", {}))
        metrics["graph_started_at"] = datetime.utcnow().isoformat()
        updated_state["processing_metrics"] = metrics

        # Invoke streaming graph
        try:
            result_state = invoke_streaming_graph(
                session_id=session_id,
                transcript=updated_state.get("transcript", ""),
                detected_language=detected_language or updated_state.get("detected_language", ""),
                state=updated_state
            )

            # Update active session tracking
            self._active_sessions[session_id] = result_state

        except Exception as e:
            logger.error(f"[Session {session_id}] Graph invocation failed: {e}", exc_info=True)
            # Return state with error
            result_state = dict(updated_state)
            result_state["error"] = str(e)
            result_state["processing_status"] = "error"

        # Format response for WebSocket
        response = self._format_response(result_state)

        exit_reason = result_state.get("exit_reason", "continue")
        logger.info(f"[Session {session_id}] Chunk #{chunk_num} processed: exit_reason={exit_reason}")

        return result_state, response

    def _format_response(self, state: StreamingEmergencyState) -> Dict[str, Any]:
        """Format graph state into WebSocket response message.

        Args:
            state: Current StreamingEmergencyState

        Returns:
            Dictionary formatted for WebSocket JSON response
        """
        exit_reason = state.get("exit_reason", "continue")

        # Determine response type
        if exit_reason == "continue":
            response_type = "partial"
        else:
            response_type = "final"

        # Build classification section
        classification = {
            "incident": {
                "type": state.get("incident_type", ""),
                "confidence": state.get("incident_confidence", 0.0),
                "reasoning": state.get("incident_reasoning", "")
            },
            "severity": {
                "level": state.get("severity_level", ""),
                "confidence": state.get("severity_confidence", 0.0),
                "reasoning": state.get("severity_reasoning", "")
            },
            "dispatch": {
                "unit": state.get("dispatch_unit", ""),
                "confidence": state.get("dispatch_confidence", 0.0),
                "priority": state.get("estimated_priority", ""),
                "reasoning": state.get("dispatch_reasoning", "")
            }
        }

        # Build evaluation section
        evaluation = {
            "overall_confidence": state.get("overall_quality_score", 0.0),
            "elapsed_seconds": state.get("elapsed_time_seconds", 0.0),
            "window_seconds": state.get("evaluation_window_seconds", 10.0),
            "exit_reason": exit_reason,
            "review_priority": state.get("review_priority", "normal"),
            "requires_human_review": state.get("requires_human_review", False),
            "concerns": state.get("concerns", []),
            "low_confidence_areas": state.get("low_confidence_areas", [])
        }

        # Build response
        response = {
            "type": response_type,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": state.get("session_id"),
            "chunk_count": state.get("chunk_count", 0),

            # Transcript
            "transcript": state.get("transcript", ""),
            "detected_language": state.get("detected_language", ""),

            # Classification results
            "classification": classification,

            # Evaluation results
            "evaluation": evaluation,

            # Processing metrics
            "processing_metrics": state.get("processing_metrics", {}),

            # Status
            "processing_status": state.get("processing_status", ""),
            "is_final": exit_reason != "continue",

            # Error if any
            "error": state.get("error")
        }

        # Add unsupported language reason if applicable
        unsupported_reason = state.get("unsupported_language_reason", "")
        if unsupported_reason:
            response["unsupported_language_reason"] = unsupported_reason

        return response

    def should_continue(self, state: StreamingEmergencyState) -> bool:
        """Check if session should continue waiting for more data.

        Args:
            state: Current streaming session state

        Returns:
            True if session should continue, False if complete
        """
        return state.get("exit_reason", "continue") == "continue"

    def get_session(self, session_id: str) -> Optional[StreamingEmergencyState]:
        """Get an active session by ID.

        Args:
            session_id: Session ID to retrieve

        Returns:
            StreamingEmergencyState if found, None otherwise
        """
        return self._active_sessions.get(session_id)

    def end_session(self, session_id: str) -> Optional[StreamingEmergencyState]:
        """End and remove an active session.

        Args:
            session_id: Session ID to end

        Returns:
            Final state of the session, or None if not found
        """
        state = self._active_sessions.pop(session_id, None)
        if state:
            logger.info(f"[Session {session_id}] Session ended")
        return state

    def get_active_session_count(self) -> int:
        """Get the number of active sessions.

        Returns:
            Number of active streaming sessions
        """
        return len(self._active_sessions)

    def prepare_for_database(self, state: StreamingEmergencyState) -> Dict[str, Any]:
        """Prepare session state for database storage.

        Args:
            state: Final streaming session state

        Returns:
            Dictionary formatted for database insertion
        """
        metrics = state.get("processing_metrics", {})

        return {
            "case_id": state.get("session_id", ""),
            "transcript": state.get("transcript", ""),
            "detected_language": state.get("detected_language", "unknown"),
            "language_confidence": state.get("language_confidence", 0.0),
            "ai_incident": state.get("incident_type", "UNKNOWN"),
            "ai_severity": state.get("severity_level", "MEDIUM"),
            "ai_unit": state.get("dispatch_unit", "POLICE"),
            "incident_confidence": state.get("incident_confidence", 0.0),
            "severity_confidence": state.get("severity_confidence", 0.0),
            "dispatch_confidence": state.get("dispatch_confidence", 0.0),
            "requires_review": True,  # ALL cases require human review
            "review_priority": state.get("review_priority", "normal"),
            "exit_reason": state.get("exit_reason", ""),
            "processing_mode": "streaming",
            "evaluation_summary": state.get("evaluation_summary", ""),
            "concerns": state.get("concerns", []),
            "processing_metrics": metrics,
            "total_processing_time_ms": metrics.get("total_processing_time_ms", 0.0),
            "stt_time_ms": metrics.get("stt_time_ms", 0.0),
            "classification_time_ms": metrics.get("classification_total_time_ms", 0.0),
            "evaluation_time_ms": metrics.get("evaluation_time_ms", 0.0),
            "chunks_processed": metrics.get("chunks_processed", 0),
            "evaluation_window_seconds": state.get("evaluation_window_seconds", 10.0),
            "unsupported_language_reason": state.get("unsupported_language_reason")
        }


def create_streaming_graph_service(config: Dict[str, Any]) -> StreamingGraphService:
    """Factory function to create StreamingGraphService from config.

    Args:
        config: Application configuration dictionary

    Returns:
        Configured StreamingGraphService instance
    """
    streaming_config = config.get("streaming", {})
    hitl_config = config.get("hitl", {})

    confidence_threshold = streaming_config.get(
        "confidence_threshold",
        hitl_config.get("confidence_threshold", 0.75)
    )
    evaluation_window = streaming_config.get("evaluation_window_seconds", 10.0)

    return StreamingGraphService(
        confidence_threshold=confidence_threshold,
        evaluation_window_seconds=evaluation_window
    )
