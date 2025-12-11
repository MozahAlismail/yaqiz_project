"""
LangGraph Workflow Definition for Emergency Dispatch

Builds and compiles the StateGraph for the emergency dispatch pipeline.
Includes checkpointing support for Human-in-the-Loop (HITL) workflows.
"""

from typing import Optional, Dict, Any
from loguru import logger

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import EmergencyState, create_initial_state
from graph.nodes import (
    init_nodes,
    stt_node,
    language_detection_node,
    incident_classification_node,
    severity_classification_node,
    dispatch_classification_node,
    self_evaluation_node,
    unsupported_language_handler_node,
    human_review_node,
    flag_for_review_node,
    complete_processing_node,
)
from graph.edges import (
    route_after_stt,
    route_after_language_detection,
    route_after_incident_classification,
    route_after_self_evaluation,
    route_after_human_review,
    create_incident_router,
)

# Global compiled graph instance
_compiled_graph = None
_checkpointer = None
_config = None


def build_emergency_graph(confidence_threshold: float = 0.75) -> StateGraph:
    """
    Build the StateGraph for the emergency dispatch pipeline.

    Creates a graph with all nodes and edges for processing emergency
    calls through the multi-agent pipeline.

    Graph Structure:
        START --> stt --> language_detection
                            |
                            +--> [unsupported] --> END
                            |
                            +--> incident_classification
                                    |
                                    +--> [human_review] --> severity_classification
                                    |
                                    +--> severity_classification --> dispatch_classification
                                                                          |
                                                                          +--> self_evaluation
                                                                                   |
                                                                                   +--> [flag_for_review] --> END
                                                                                   |
                                                                                   +--> complete_processing --> END

    Args:
        confidence_threshold: Confidence threshold for routing to human review

    Returns:
        Configured StateGraph (not yet compiled)
    """
    logger.info(f"Building emergency dispatch graph with confidence_threshold={confidence_threshold}")

    # Create the graph with EmergencyState schema
    graph = StateGraph(EmergencyState)

    # Add all nodes
    graph.add_node("stt", stt_node)
    graph.add_node("language_detection", language_detection_node)
    graph.add_node("incident_classification", incident_classification_node)
    graph.add_node("severity_classification", severity_classification_node)
    graph.add_node("dispatch_classification", dispatch_classification_node)
    graph.add_node("self_evaluation", self_evaluation_node)
    graph.add_node("unsupported_language_handler", unsupported_language_handler_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("flag_for_review", flag_for_review_node)
    graph.add_node("complete_processing", complete_processing_node)

    # Set entry point
    graph.set_entry_point("stt")

    # Add conditional edge after STT
    graph.add_conditional_edges(
        "stt",
        route_after_stt,
        {
            "language_detection": "language_detection",
            "end": END,
        }
    )

    # Add conditional edge after language detection
    graph.add_conditional_edges(
        "language_detection",
        route_after_language_detection,
        {
            "incident_classification": "incident_classification",
            "unsupported_language_handler": "unsupported_language_handler",
        }
    )

    # Unsupported language handler goes to END
    graph.add_edge("unsupported_language_handler", END)

    # Add conditional edge after incident classification
    incident_router = create_incident_router(confidence_threshold)
    graph.add_conditional_edges(
        "incident_classification",
        incident_router,
        {
            "severity_classification": "severity_classification",
            "human_review": "human_review",
        }
    )

    # Human review continues to severity classification (to generate full predictions)
    graph.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "severity_classification": "severity_classification",
            "end": END,
        }
    )

    # Sequential edges for main classification flow
    graph.add_edge("severity_classification", "dispatch_classification")
    graph.add_edge("dispatch_classification", "self_evaluation")

    # Add conditional edge after self-evaluation
    graph.add_conditional_edges(
        "self_evaluation",
        route_after_self_evaluation,
        {
            "flag_for_review": "flag_for_review",
            "complete_processing": "complete_processing",
        }
    )

    # Final nodes go to END
    graph.add_edge("flag_for_review", END)
    graph.add_edge("complete_processing", END)

    logger.info("Emergency dispatch graph built successfully")
    return graph


def create_emergency_graph(
    stt_model,
    language_model,
    incident_classifier,
    severity_classifier,
    dispatch_classifier,
    config: dict,
    enable_checkpointing: bool = True
):
    """
    Create and compile the emergency dispatch graph with all dependencies.

    This is the main initialization function that should be called during
    application startup. It initializes nodes with models and compiles
    the graph with optional checkpointing.

    Args:
        stt_model: STT model instance
        language_model: Language detection model instance
        incident_classifier: Incident classifier instance
        severity_classifier: Severity classifier instance
        dispatch_classifier: Dispatch classifier instance
        config: Application configuration dictionary
        enable_checkpointing: Whether to enable checkpoint saving

    Returns:
        Compiled graph ready for invocation
    """
    global _compiled_graph, _checkpointer, _config

    _config = config

    # Initialize nodes with model dependencies
    init_nodes(
        stt_model=stt_model,
        language_model=language_model,
        incident_classifier=incident_classifier,
        severity_classifier=severity_classifier,
        dispatch_classifier=dispatch_classifier,
        config=config
    )

    # Get confidence threshold from config
    confidence_threshold = config.get("hitl", {}).get("confidence_threshold", 0.75)

    # Build the graph
    graph = build_emergency_graph(confidence_threshold)

    # Setup checkpointer for HITL workflows
    if enable_checkpointing:
        _checkpointer = MemorySaver()
        _compiled_graph = graph.compile(checkpointer=_checkpointer)
        logger.info("Emergency graph compiled with checkpointing enabled")
    else:
        _compiled_graph = graph.compile()
        logger.info("Emergency graph compiled without checkpointing")

    return _compiled_graph


def get_emergency_graph():
    """
    Get the compiled emergency dispatch graph singleton.

    Returns:
        Compiled graph instance

    Raises:
        RuntimeError: If graph has not been initialized
    """
    if _compiled_graph is None:
        raise RuntimeError(
            "Emergency graph not initialized. Call create_emergency_graph() first."
        )
    return _compiled_graph


def get_checkpointer():
    """
    Get the checkpointer instance.

    Returns:
        MemorySaver checkpointer instance or None if checkpointing disabled
    """
    return _checkpointer


def invoke_graph(
    audio_path: str,
    case_id: str,
    config: Optional[Dict[str, Any]] = None
) -> EmergencyState:
    """
    Invoke the emergency dispatch graph with initial state.

    Convenience function to run the full pipeline on an audio file.

    Args:
        audio_path: Path to the audio file to process
        case_id: Unique identifier for this emergency case
        config: Optional LangGraph config (for thread_id, etc.)

    Returns:
        Final EmergencyState after pipeline completion
    """
    graph = get_emergency_graph()
    initial_state = create_initial_state(audio_path, case_id)

    if config is None:
        config = {"configurable": {"thread_id": case_id}}

    logger.info(f"Invoking emergency graph for case {case_id}")
    result = graph.invoke(initial_state, config)
    logger.info(f"Emergency graph completed for case {case_id}")

    return result


def invoke_graph_with_checkpoint(
    audio_path: str,
    case_id: str
) -> tuple[EmergencyState, str]:
    """
    Invoke the graph with checkpointing enabled.

    Useful for HITL workflows where the graph may be paused
    and resumed after human review.

    Args:
        audio_path: Path to the audio file to process
        case_id: Unique identifier for this emergency case

    Returns:
        Tuple of (final state, checkpoint_id)
    """
    graph = get_emergency_graph()
    initial_state = create_initial_state(audio_path, case_id)

    config = {"configurable": {"thread_id": case_id}}

    result = graph.invoke(initial_state, config)

    # Return the case_id as checkpoint identifier
    return result, case_id


def resume_from_checkpoint(
    checkpoint_id: str,
    updated_state: Optional[Dict[str, Any]] = None
) -> EmergencyState:
    """
    Resume workflow from a checkpoint after human review.

    Used in HITL workflows to continue processing after a human
    has reviewed and potentially modified the state.

    Args:
        checkpoint_id: The checkpoint/thread ID to resume from
        updated_state: Optional state updates from human review

    Returns:
        Final EmergencyState after resumption
    """
    if _checkpointer is None:
        raise RuntimeError("Checkpointing not enabled. Cannot resume from checkpoint.")

    graph = get_emergency_graph()
    config = {"configurable": {"thread_id": checkpoint_id}}

    # Get the current state from checkpoint
    state_snapshot = graph.get_state(config)
    current_state = dict(state_snapshot.values)

    # Apply any updates from human review
    if updated_state:
        current_state.update(updated_state)
        logger.info(f"Applied human review updates to state for checkpoint {checkpoint_id}")

    # Resume the graph with updated state
    result = graph.invoke(current_state, config)

    logger.info(f"Resumed and completed graph from checkpoint {checkpoint_id}")
    return result


def get_graph_state(checkpoint_id: str) -> Optional[EmergencyState]:
    """
    Get the current state for a checkpoint.

    Useful for retrieving state for display during human review.

    Args:
        checkpoint_id: The checkpoint/thread ID

    Returns:
        Current EmergencyState or None if not found
    """
    if _checkpointer is None:
        logger.warning("Checkpointing not enabled")
        return None

    graph = get_emergency_graph()
    config = {"configurable": {"thread_id": checkpoint_id}}

    try:
        state_snapshot = graph.get_state(config)
        return dict(state_snapshot.values) if state_snapshot else None
    except Exception as e:
        logger.error(f"Failed to get state for checkpoint {checkpoint_id}: {e}")
        return None


def stream_graph(
    audio_path: str,
    case_id: str
):
    """
    Stream graph execution for intermediate results.

    Yields state updates as each node completes, useful for
    providing real-time progress updates to clients.

    Args:
        audio_path: Path to the audio file to process
        case_id: Unique identifier for this emergency case

    Yields:
        Tuple of (node_name, state_update) for each node execution
    """
    graph = get_emergency_graph()
    initial_state = create_initial_state(audio_path, case_id)
    config = {"configurable": {"thread_id": case_id}}

    logger.info(f"Streaming emergency graph for case {case_id}")

    for event in graph.stream(initial_state, config):
        for node_name, state_update in event.items():
            logger.debug(f"[Stream] Node '{node_name}' completed")
            yield node_name, state_update

    logger.info(f"Streaming completed for case {case_id}")
