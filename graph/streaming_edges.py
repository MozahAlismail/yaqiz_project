"""
Streaming LangGraph Conditional Edge Functions

Defines routing logic for the streaming emergency dispatch workflow.
These functions determine which node to execute next based on
streaming-specific state values.

NOTE: Language detection routing removed. Language is now forced at the
WebSocket/STT level via --language parameter (ar or en).

IMPORTANT: This file is SEPARATE from graph/edges.py - does NOT modify it.
"""

from typing import Literal
from loguru import logger

from graph.streaming_state import StreamingEmergencyState


# ═══════════════════════════════════════════════════════════════════════════
# STREAMING ROUTING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

# NOTE: route_after_streaming_language_detection() removed.
# Language is now forced at WebSocket/STT level via --language parameter.
# def route_after_streaming_language_detection(
#     state: StreamingEmergencyState
# ) -> Literal["incident_classification", "unsupported_language_handler"]:
#     """
#     Route after language detection in streaming workflow.

#     If the detected language is not supported, route to the
#     unsupported language handler. Otherwise, continue to
#     incident classification.

#     Args:
#         state: Current StreamingEmergencyState after language detection

#     Returns:
#         Next node name: "incident_classification" or "unsupported_language_handler"
#     """
#     is_supported = state.get("is_supported", False)

#     if not is_supported:
#         logger.info(f"[Streaming Router] Language not supported: {state.get('detected_language')}, "
#                     "routing to unsupported_language_handler")
#         return "unsupported_language_handler"

#     logger.debug("[Streaming Router] Language supported, routing to incident_classification")
#     return "incident_classification"

def route_after_confidence_gate(
    state: StreamingEmergencyState
) -> Literal["streaming_complete", "continue_evaluation"]:
    """
    Route after confidence gate node in streaming workflow.

    Determines whether to:
    1. Complete and send to human review (confidence_met, critical_severity, timeout)
    2. Continue waiting for more audio data (continue)

    Args:
        state: Current StreamingEmergencyState after confidence gate

    Returns:
        Next node name: "streaming_complete" or "continue_evaluation"
    """
    exit_reason = state.get("exit_reason", "continue")

    if exit_reason == "continue":
        logger.debug("[Streaming Router] Continue waiting for more audio data")
        return "continue_evaluation"

    # All other exit reasons go to streaming_complete
    logger.info(f"[Streaming Router] Exit reason: {exit_reason}, routing to streaming_complete")
    return "streaming_complete"


def should_exit_streaming(state: StreamingEmergencyState) -> bool:
    """
    Check if streaming should exit based on exit_reason.

    Helper function to determine if the streaming loop should exit.

    Args:
        state: Current StreamingEmergencyState

    Returns:
        True if streaming should exit, False to continue
    """
    exit_reason = state.get("exit_reason", "continue")
    return exit_reason != "continue"


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

# NOTE: create_streaming_language_router() removed.
# Language is now forced at WebSocket/STT level via --language parameter.
# def create_streaming_language_router():
#     """
#     Create a language router for streaming workflow.

#     Factory function that returns a router function.

#     Returns:
#         Router function for language detection
#     """
#     def router(state: StreamingEmergencyState) -> Literal["incident_classification", "unsupported_language_handler"]:
#         return route_after_streaming_language_detection(state)

#     return router

def create_confidence_gate_router():
    """
    Create a confidence gate router for streaming workflow.

    Factory function that returns a router function.

    Returns:
        Router function for confidence gate
    """
    def router(state: StreamingEmergencyState) -> Literal["streaming_complete", "continue_evaluation"]:
        return route_after_confidence_gate(state)

    return router


# ═══════════════════════════════════════════════════════════════════════════
# ROUTING CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# Node names for streaming workflow
# NOTE: Language detection nodes removed - language forced at WebSocket/STT level
# NODE_LANGUAGE_DETECTION = "language_detection"
NODE_INCIDENT_CLASSIFICATION = "incident_classification"
NODE_SEVERITY_CLASSIFICATION = "severity_classification"
NODE_DISPATCH_CLASSIFICATION = "dispatch_classification"
NODE_CONFIDENCE_GATE = "confidence_gate"
# NODE_UNSUPPORTED_LANGUAGE = "unsupported_language_handler"
NODE_STREAMING_COMPLETE = "streaming_complete"
NODE_CONTINUE_EVALUATION = "continue_evaluation"
NODE_END = "end"

# Exit reasons
EXIT_CONFIDENCE_MET = "confidence_met"
EXIT_CRITICAL_SEVERITY = "critical_severity"
EXIT_TIMEOUT = "timeout"

# EXIT_UNSUPPORTED_LANGUAGE = "unsupported_language"
EXIT_CONTINUE = "continue"

# Review priorities
PRIORITY_URGENT = "urgent"
PRIORITY_HIGH = "high"
PRIORITY_NORMAL = "normal"

# Conditional edge mappings for clarity
# LANGUAGE_DETECTION_ROUTES = {
#     "incident_classification": NODE_INCIDENT_CLASSIFICATION,
#     "unsupported_language_handler": NODE_UNSUPPORTED_LANGUAGE,
# }

CONFIDENCE_GATE_ROUTES = {
    "streaming_complete": NODE_STREAMING_COMPLETE,
    "continue_evaluation": NODE_CONTINUE_EVALUATION,
}