"""Agent Controller - Orchestrates all AI agents using LangGraph workflow"""

import logging
import uuid
from typing import Dict, Any, Optional, Generator

from agents.stt_agent import STTAgent
from agents.language_detection_agent import LanguageDetectionAgent
from agents.incident_agent import IncidentAgent
from agents.severity_agent import SeverityAgent
from agents.dispatch_agent import DispatchAgent
from agents.self_eval_agent import SelfEvaluationAgent

# LangGraph imports
from graph.workflow import (
    get_emergency_graph,
    invoke_graph,
    invoke_graph_with_checkpoint,
    resume_from_checkpoint,
    get_graph_state,
    stream_graph,
)
from graph.state import create_initial_state

logger = logging.getLogger(__name__)


class AgentController:
    """
    Orchestrates the multi-agent pipeline for emergency dispatch.

    This controller now uses LangGraph for workflow orchestration,
    providing stateful execution, conditional routing, and HITL
    checkpointing support. The legacy sequential pipeline is still
    available via the use_legacy_pipeline flag.
    """

    def __init__(
        self,
        stt_agent: STTAgent,
        language_agent: LanguageDetectionAgent,
        incident_agent: IncidentAgent,
        severity_agent: SeverityAgent,
        dispatch_agent: DispatchAgent,
        self_eval_agent: SelfEvaluationAgent,
        use_legacy_pipeline: bool = False
    ):
        """
        Initialize the agent controller.

        Args:
            stt_agent: Speech-to-text agent
            language_agent: Language detection agent
            incident_agent: Incident classification agent
            severity_agent: Severity classification agent
            dispatch_agent: Dispatch classification agent
            self_eval_agent: Self-evaluation agent
            use_legacy_pipeline: If True, use sequential pipeline instead of LangGraph
        """
        self.stt_agent = stt_agent
        self.language_agent = language_agent
        self.incident_agent = incident_agent
        self.severity_agent = severity_agent
        self.dispatch_agent = dispatch_agent
        self.self_eval_agent = self_eval_agent
        self.use_legacy_pipeline = use_legacy_pipeline
        logger.info(f"Agent Controller initialized (LangGraph mode: {not use_legacy_pipeline})")

    def process_emergency_call(
        self,
        audio_path: str,
        case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process emergency call through the agent pipeline.

        Uses LangGraph workflow by default, with fallback to legacy
        sequential pipeline if configured.

        Args:
            audio_path: Path to audio file
            case_id: Optional case identifier (auto-generated if not provided)

        Returns:
            Complete analysis results compatible with existing API
        """
        if case_id is None:
            case_id = str(uuid.uuid4())

        logger.info(f"Processing emergency call: {audio_path} (case: {case_id})")

        if self.use_legacy_pipeline:
            return self._process_legacy(audio_path)

        return self._process_with_graph(audio_path, case_id)

    def _process_with_graph(self, audio_path: str, case_id: str) -> Dict[str, Any]:
        """
        Process emergency call using LangGraph workflow.

        Args:
            audio_path: Path to audio file
            case_id: Case identifier

        Returns:
            Complete analysis results
        """
        try:
            # Invoke the LangGraph workflow
            result = invoke_graph(audio_path, case_id)

            # Convert LangGraph state to API response format
            return self._convert_graph_result_to_response(result)

        except Exception as e:
            logger.error(f"LangGraph processing failed: {e}")
            # Fallback to legacy pipeline on graph error
            logger.info("Falling back to legacy pipeline")
            return self._process_legacy(audio_path)

    def _convert_graph_result_to_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert LangGraph state to API response format.

        Ensures backward compatibility with existing API consumers
        by maintaining the same response structure.

        Args:
            state: Final EmergencyState from graph execution

        Returns:
            Response dict in legacy format
        """
        # Build evaluation dict for compatibility
        evaluation = {
            "status": "success" if not state.get("error") else "error",
            "overall_quality_score": state.get("overall_quality_score", 0.0),
            "requires_human_review": state.get("requires_human_review", False),
            "concerns": state.get("concerns", []),
            "evaluation_summary": state.get("evaluation_summary", "")
        }

        return {
            "transcript": state.get("transcript", ""),
            "detected_language": state.get("detected_language", ""),
            "language_confidence": state.get("language_confidence", 0.0),
            "incident_type": state.get("incident_type", ""),
            "incident_confidence": state.get("incident_confidence", 0.0),
            "severity_level": state.get("severity_level", ""),
            "severity_confidence": state.get("severity_confidence", 0.0),
            "dispatch_unit": state.get("dispatch_unit", ""),
            "dispatch_confidence": state.get("dispatch_confidence", 0.0),
            "evaluation": evaluation,
            "requires_human_review": state.get("requires_human_review", False),
            "processing_status": state.get("processing_status", "completed"),
            # Additional fields from graph state
            "incident_reasoning": state.get("incident_reasoning", ""),
            "severity_reasoning": state.get("severity_reasoning", ""),
            "dispatch_reasoning": state.get("dispatch_reasoning", ""),
            "keywords_found": state.get("keywords_found", []),
            "urgency_indicators": state.get("urgency_indicators", []),
            "estimated_priority": state.get("estimated_priority", ""),
            "error": state.get("error"),
        }

    def _process_legacy(self, audio_path: str) -> Dict[str, Any]:
        """
        Process emergency call using legacy sequential pipeline.

        Preserved for backward compatibility and fallback scenarios.

        Args:
            audio_path: Path to audio file

        Returns:
            Complete analysis results
        """
        logger.info(f"Processing emergency call (legacy): {audio_path}")

        # Step 1: Speech-to-Text
        stt_result = self.stt_agent.process(audio_path)
        if stt_result["status"] != "success":
            return {"error": "STT failed", "details": stt_result}

        transcript = stt_result["transcript"]
        detected_language = stt_result.get("detected_language", "en")

        # Step 2: Language Detection (verify)
        lang_result = self.language_agent.process(transcript)
        if lang_result["status"] == "success":
            detected_language = lang_result["language"]

        # Step 3: Incident Classification
        incident_result = self.incident_agent.process(transcript, detected_language)

        # Step 4: Severity Classification
        severity_result = self.severity_agent.process(
            transcript,
            incident_result.get("incident_type", "UNKNOWN"),
            detected_language
        )

        # Step 5: Dispatch Classification
        dispatch_result = self.dispatch_agent.process(
            transcript,
            incident_result.get("incident_type", "UNKNOWN"),
            severity_result.get("severity_level", "MEDIUM"),
            detected_language
        )

        # Step 6: Self-Evaluation
        eval_result = self.self_eval_agent.process(
            transcript,
            incident_result,
            severity_result,
            dispatch_result
        )

        # Compile complete result
        complete_result = {
            "transcript": transcript,
            "detected_language": detected_language,
            "language_confidence": lang_result.get("confidence", 0.0),
            "incident_type": incident_result.get("incident_type"),
            "incident_confidence": incident_result.get("confidence", 0.0),
            "severity_level": severity_result.get("severity_level"),
            "severity_confidence": severity_result.get("confidence", 0.0),
            "dispatch_unit": dispatch_result.get("dispatch_unit"),
            "dispatch_confidence": dispatch_result.get("confidence", 0.0),
            "evaluation": eval_result,
            "requires_human_review": eval_result.get("requires_human_review", False),
            "processing_status": "completed"
        }

        logger.info("Emergency call processing completed (legacy)")
        return complete_result

    # =========================================================================
    # LangGraph-specific methods
    # =========================================================================

    def process_with_checkpoint(
        self,
        audio_path: str,
        case_id: Optional[str] = None
    ) -> tuple[Dict[str, Any], str]:
        """
        Process emergency call with checkpoint for HITL workflows.

        Enables pausing and resuming the workflow after human review.

        Args:
            audio_path: Path to audio file
            case_id: Optional case identifier

        Returns:
            Tuple of (result dict, checkpoint_id)
        """
        if case_id is None:
            case_id = str(uuid.uuid4())

        logger.info(f"Processing with checkpoint: {audio_path} (case: {case_id})")

        state, checkpoint_id = invoke_graph_with_checkpoint(audio_path, case_id)
        result = self._convert_graph_result_to_response(state)

        return result, checkpoint_id

    def resume_from_review(
        self,
        checkpoint_id: str,
        human_corrections: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resume workflow after human review.

        Continues processing from a checkpoint with optional corrections
        from human reviewers.

        Args:
            checkpoint_id: Checkpoint/case ID to resume from
            human_corrections: Optional dict with corrected values

        Returns:
            Final analysis results after resumption
        """
        logger.info(f"Resuming from checkpoint: {checkpoint_id}")

        state = resume_from_checkpoint(checkpoint_id, human_corrections)
        return self._convert_graph_result_to_response(state)

    def get_case_state(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current state for a case from checkpoint.

        Useful for displaying current state during human review.

        Args:
            case_id: Case/checkpoint identifier

        Returns:
            Current state dict or None if not found
        """
        state = get_graph_state(case_id)
        if state:
            return self._convert_graph_result_to_response(state)
        return None

    def stream_emergency_call(
        self,
        audio_path: str,
        case_id: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream emergency call processing with intermediate results.

        Yields updates as each node in the graph completes, enabling
        real-time progress updates for clients.

        Args:
            audio_path: Path to audio file
            case_id: Optional case identifier

        Yields:
            Dict with node_name and partial state update for each step
        """
        if case_id is None:
            case_id = str(uuid.uuid4())

        logger.info(f"Streaming emergency call: {audio_path} (case: {case_id})")

        for node_name, state_update in stream_graph(audio_path, case_id):
            yield {
                "node": node_name,
                "update": state_update,
                "case_id": case_id
            }
