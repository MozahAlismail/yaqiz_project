"""
Streaming LangGraph Workflow Definition for Emergency Dispatch

Builds and compiles the StateGraph for streaming emergency dispatch.
Features:
- Time-bounded confidence evaluation (10-second window)
- Priority-based human review queue (ALL cases require review)
- Processing time metrics tracking
- Language selection via WebSocket parameter (ar/en)

NOTE: Language detection node removed. Language is now forced at the
WebSocket/STT level via --language parameter (ar or en).
# - Unsupported language handling
IMPORTANT: This is a SEPARATE workflow from graph/workflow.py
It does NOT modify the existing batch workflow.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.streaming_state import (
    StreamingEmergencyState,
    create_streaming_initial_state,
    update_streaming_state_with_transcript
)
from graph.streaming_nodes import (
    # streaming_language_detection_node,
    streaming_incident_classification_node,
    streaming_severity_classification_node,
    streaming_dispatch_classification_node,
    # streaming_unsupported_language_handler_node,
    confidence_gate_node,
    streaming_complete_node
)
from graph.streaming_edges import (
    # route_after_streaming_language_detection,
    route_after_confidence_gate,
    should_exit_streaming
)

# Import node initialization from base nodes
from graph.nodes import init_nodes


# Global compiled graph instances
_streaming_graph = None
_streaming_checkpointer = None
_streaming_config = None


# ═══════════════════════════════════════════════════════════════════════════
# GRAPH BUILDING
# ═══════════════════════════════════════════════════════════════════════════

def build_streaming_graph(
    confidence_threshold: float = 0.75,
    evaluation_window_seconds: float = 10.0
) -> StateGraph:
    """
    Build the StateGraph for streaming emergency dispatch pipeline.

    Creates a graph with all nodes and edges for processing live
    microphone audio through the streaming pipeline.

    NOTE: Language is now selected via WebSocket parameter (--language ar/en).
    No in-graph language detection is performed.

    Graph Structure:
        START --> incident_classification
                        |
                        +--> severity_classification
                                |
                                +--> dispatch_classification
                                        |
                                        +--> confidence_gate
                                                |
                                                +--> [continue] --> (wait for more data)
                                                |
                                                +--> [exit] --> streaming_complete --> END

    Args:
        confidence_threshold: Confidence threshold for evaluation (default: 0.75)
        evaluation_window_seconds: Max time for evaluation (default: 10.0)

    Returns:
        Configured StateGraph (not yet compiled)
    """
    logger.info(f"Building streaming graph: threshold={confidence_threshold}, "
                f"window={evaluation_window_seconds}s")

    # Create the graph with StreamingEmergencyState schema
    graph = StateGraph(StreamingEmergencyState)

    # Add classification nodes (language detection removed - handled at STT level)
    # graph.add_node("language_detection", streaming_language_detection_node)
    graph.add_node("incident_classification", streaming_incident_classification_node)
    graph.add_node("severity_classification", streaming_severity_classification_node)
    graph.add_node("dispatch_classification", streaming_dispatch_classification_node)
    graph.add_node("confidence_gate", confidence_gate_node)
    # graph.add_node("unsupported_language_handler", streaming_unsupported_language_handler_node)    
    graph.add_node("streaming_complete", streaming_complete_node)

    # Set entry point - directly to incident classification
    # Language is now forced via WebSocket parameter (ar/en)
    graph.set_entry_point("incident_classification")
    # graph.set_entry_point("language_detection")

    # # Add conditional edge after language detection
    # graph.add_conditional_edges(
    #     "language_detection",
    #     route_after_streaming_language_detection,
    #     {
    #         "incident_classification": "incident_classification",
    #         "unsupported_language_handler": "unsupported_language_handler",
    #     }
    # )

    # # Unsupported language handler goes to streaming_complete
    # graph.add_edge("unsupported_language_handler", "streaming_complete")
    
    # Sequential edges for classification flow
    graph.add_edge("incident_classification", "severity_classification")
    graph.add_edge("severity_classification", "dispatch_classification")
    graph.add_edge("dispatch_classification", "confidence_gate")

    # Confidence gate routing
    graph.add_conditional_edges(
        "confidence_gate",
        route_after_confidence_gate,
        {
            "streaming_complete": "streaming_complete",
            "continue_evaluation": END,  # Exit to wait for more data
        }
    )

    # Streaming complete goes to END
    graph.add_edge("streaming_complete", END)

    logger.info("Streaming graph built successfully")
    return graph


# ═══════════════════════════════════════════════════════════════════════════
# GRAPH CREATION AND INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def create_streaming_graph(
    language_model,
    incident_classifier,
    severity_classifier,
    dispatch_classifier,
    config: dict,
    enable_checkpointing: bool = True
):
    """
    Create and compile the streaming emergency dispatch graph.

    This is the main initialization function that should be called during
    application startup. It initializes nodes with models and compiles
    the graph with optional checkpointing.

    Args:
        language_model: Language detection model instance
        incident_classifier: Incident classifier instance
        severity_classifier: Severity classifier instance
        dispatch_classifier: Dispatch classifier instance
        config: Application configuration dictionary
        enable_checkpointing: Whether to enable checkpoint saving

    Returns:
        Compiled graph ready for invocation
    """
    global _streaming_graph, _streaming_checkpointer, _streaming_config

    _streaming_config = config

    # Initialize nodes with model dependencies (shared with batch workflow)
    # This ensures both workflows use the same models
    init_nodes(
        language_model=language_model,
        incident_classifier=incident_classifier,
        severity_classifier=severity_classifier,
        dispatch_classifier=dispatch_classifier,
        config=config
    )

    # Get streaming configuration
    streaming_config = config.get("streaming", {})
    confidence_threshold = streaming_config.get(
        "confidence_threshold",
        config.get("hitl", {}).get("confidence_threshold", 0.75)
    )
    evaluation_window = streaming_config.get("evaluation_window_seconds", 10.0)

    # Build the graph
    graph = build_streaming_graph(
        confidence_threshold=confidence_threshold,
        evaluation_window_seconds=evaluation_window
    )

    # Setup checkpointer for HITL workflows
    if enable_checkpointing:
        _streaming_checkpointer = MemorySaver()
        _streaming_graph = graph.compile(checkpointer=_streaming_checkpointer)
        logger.info("Streaming graph compiled with checkpointing enabled")
    else:
        _streaming_graph = graph.compile()
        logger.info("Streaming graph compiled without checkpointing")

    return _streaming_graph


def get_streaming_graph():
    """
    Get the compiled streaming graph singleton.

    Returns:
        Compiled graph instance

    Raises:
        RuntimeError: If graph has not been initialized
    """
    if _streaming_graph is None:
        raise RuntimeError(
            "Streaming graph not initialized. Call create_streaming_graph() first."
        )
    return _streaming_graph


def get_streaming_checkpointer():
    """
    Get the streaming checkpointer instance.

    Returns:
        MemorySaver checkpointer instance or None if checkpointing disabled
    """
    return _streaming_checkpointer


# ═══════════════════════════════════════════════════════════════════════════
# STREAMING INVOCATION
# ═══════════════════════════════════════════════════════════════════════════

def invoke_streaming_graph(
    session_id: str,
    transcript: str,
    detected_language: str = "",
    state: Optional[StreamingEmergencyState] = None,
    config: Optional[Dict[str, Any]] = None
) -> StreamingEmergencyState:
    """
    Invoke the streaming graph with initial or updated state.

    This function can be called:
    1. Initially with a new transcript chunk to start processing
    2. With accumulated state to continue processing

    Args:
        session_id: Unique WebSocket session identifier
        transcript: Transcript text to process
        detected_language: Language detected by Whisper STT
        state: Existing state to update (None for new session)
        config: Optional LangGraph config (for thread_id, etc.)

    Returns:
        Updated StreamingEmergencyState after graph execution
    """
    graph = get_streaming_graph()

    # Create initial state or update existing
    if state is None:
        # Get config values
        streaming_config = _streaming_config.get("streaming", {}) if _streaming_config else {}
        confidence_threshold = streaming_config.get(
            "confidence_threshold",
            _streaming_config.get("hitl", {}).get("confidence_threshold", 0.75) if _streaming_config else 0.75
        )
        evaluation_window = streaming_config.get("evaluation_window_seconds", 10.0)

        initial_state = create_streaming_initial_state(
            session_id=session_id,
            transcript=transcript,
            detected_language=detected_language,
            confidence_threshold=confidence_threshold,
            evaluation_window_seconds=evaluation_window
        )

        # Set graph started time
        metrics = dict(initial_state.get("processing_metrics", {}))
        metrics["graph_started_at"] = datetime.utcnow().isoformat()
        initial_state["processing_metrics"] = metrics
    else:
        # Update existing state with new transcript
        initial_state = update_streaming_state_with_transcript(
            state=state,
            new_transcript_chunk=transcript,
            detected_language=detected_language,
            chunk_received_at=datetime.utcnow().isoformat()
        )

    if config is None:
        config = {"configurable": {"thread_id": session_id}}

    logger.info(f"Invoking streaming graph for session {session_id}")
    result = graph.invoke(initial_state, config)
    logger.info(f"Streaming graph completed for session {session_id}, "
                f"exit_reason: {result.get('exit_reason')}")

    return result


def stream_streaming_graph(
    session_id: str,
    transcript: str,
    detected_language: str = "",
    state: Optional[StreamingEmergencyState] = None
):
    """
    Stream graph execution for intermediate results.

    Yields state updates as each node completes.

    Args:
        session_id: Unique WebSocket session identifier
        transcript: Transcript text to process
        detected_language: Language detected by Whisper STT
        state: Existing state to update (None for new session)

    Yields:
        Tuple of (node_name, state_update) for each node execution
    """
    graph = get_streaming_graph()

    # Create initial state or update existing
    if state is None:
        streaming_config = _streaming_config.get("streaming", {}) if _streaming_config else {}
        confidence_threshold = streaming_config.get(
            "confidence_threshold",
            _streaming_config.get("hitl", {}).get("confidence_threshold", 0.75) if _streaming_config else 0.75
        )
        evaluation_window = streaming_config.get("evaluation_window_seconds", 10.0)

        initial_state = create_streaming_initial_state(
            session_id=session_id,
            transcript=transcript,
            detected_language=detected_language,
            confidence_threshold=confidence_threshold,
            evaluation_window_seconds=evaluation_window
        )

        metrics = dict(initial_state.get("processing_metrics", {}))
        metrics["graph_started_at"] = datetime.utcnow().isoformat()
        initial_state["processing_metrics"] = metrics
    else:
        initial_state = update_streaming_state_with_transcript(
            state=state,
            new_transcript_chunk=transcript,
            detected_language=detected_language,
            chunk_received_at=datetime.utcnow().isoformat()
        )

    config = {"configurable": {"thread_id": session_id}}

    logger.info(f"Streaming graph execution for session {session_id}")

    for event in graph.stream(initial_state, config):
        for node_name, state_update in event.items():
            logger.debug(f"[Stream] Node '{node_name}' completed")
            yield node_name, state_update


# ═══════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

def get_streaming_state(session_id: str) -> Optional[StreamingEmergencyState]:
    """
    Get the current state for a streaming session.

    Useful for retrieving state during human review.

    Args:
        session_id: The session/thread ID

    Returns:
        Current StreamingEmergencyState or None if not found
    """
    if _streaming_checkpointer is None:
        logger.warning("Streaming checkpointing not enabled")
        return None

    graph = get_streaming_graph()
    config = {"configurable": {"thread_id": session_id}}

    try:
        state_snapshot = graph.get_state(config)
        return dict(state_snapshot.values) if state_snapshot else None
    except Exception as e:
        logger.error(f"Failed to get state for session {session_id}: {e}")
        return None


def check_streaming_exit(state: StreamingEmergencyState) -> bool:
    """
    Check if streaming workflow should exit.

    Convenience function for external code to check exit status.

    Args:
        state: Current StreamingEmergencyState

    Returns:
        True if streaming should exit, False to continue
    """
    return should_exit_streaming(state)


def get_review_priority(state: StreamingEmergencyState) -> str:
    """
    Get the human review priority from state.

    Args:
        state: Current StreamingEmergencyState

    Returns:
        Review priority: "urgent", "high", or "normal"
    """
    return state.get("review_priority", "normal")


def prepare_case_for_database(state: StreamingEmergencyState) -> Dict[str, Any]:
    """
    Prepare streaming state for database storage.

    Extracts and formats the relevant fields for saving to the cases table.

    Args:
        state: Final StreamingEmergencyState

    Returns:
        Dictionary ready for database insertion
    """
    return {
        "case_id": state.get("session_id", ""),
        "transcript": state.get("transcript", ""),
        "detected_language": state.get("detected_language", ""),
        "language_confidence": state.get("language_confidence", 0.0),
        "ai_incident": state.get("incident_type", ""),
        "ai_severity": state.get("severity_level", ""),
        "ai_unit": state.get("dispatch_unit", ""),
        "incident_confidence": state.get("incident_confidence", 0.0),
        "severity_confidence": state.get("severity_confidence", 0.0),
        "dispatch_confidence": state.get("dispatch_confidence", 0.0),
        "requires_review": state.get("requires_human_review", True),
        # Streaming-specific fields
        "review_priority": state.get("review_priority", "normal"),
        "exit_reason": state.get("exit_reason", ""),
        "processing_mode": "streaming",
        "processing_metrics": state.get("processing_metrics", {}),
        "evaluation_summary": state.get("evaluation_summary", ""),
        "concerns": state.get("concerns", []),
    }