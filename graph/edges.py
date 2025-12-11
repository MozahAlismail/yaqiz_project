"""
Conditional Edge Functions for Emergency Dispatch LangGraph

Defines routing logic for conditional edges in the workflow graph.
These functions determine which node to execute next based on the
current state values.
"""

from typing import Literal
from loguru import logger

from graph.state import EmergencyState


# Default confidence threshold for routing decisions
DEFAULT_CONFIDENCE_THRESHOLD = 0.75


def route_after_stt(state: EmergencyState) -> Literal["language_detection", "end"]:
    """
    Route after STT node completion.

    If STT failed (error present and no transcript), route to end.
    Otherwise, continue to language detection.

    Args:
        state: Current EmergencyState after STT node

    Returns:
        Next node name: "language_detection" or "end"
    """
    if state.get("error") and not state.get("transcript"):
        logger.warning(f"[Router] STT failed, ending pipeline: {state.get('error')}")
        return "end"

    logger.debug("[Router] STT successful, routing to language_detection")
    return "language_detection"


def route_after_language_detection(
    state: EmergencyState
) -> Literal["incident_classification", "unsupported_language_handler"]:
    """
    Route after language detection node.

    If the detected language is not supported, route to the
    unsupported language handler. Otherwise, continue to
    incident classification.

    Args:
        state: Current EmergencyState after language detection

    Returns:
        Next node name: "incident_classification" or "unsupported_language_handler"
    """
    is_supported = state.get("is_supported", False)

    if not is_supported:
        logger.info(f"[Router] Language not supported: {state.get('detected_language')}, "
                   "routing to unsupported_language_handler")
        return "unsupported_language_handler"

    logger.debug("[Router] Language supported, routing to incident_classification")
    return "incident_classification"


def route_after_incident_classification(
    state: EmergencyState,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
) -> Literal["severity_classification", "human_review"]:
    """
    Route after incident classification node.

    If incident classification confidence is below threshold,
    route to human review. Otherwise, continue to severity
    classification.

    Args:
        state: Current EmergencyState after incident classification
        confidence_threshold: Minimum confidence to continue without review

    Returns:
        Next node name: "severity_classification" or "human_review"
    """
    confidence = state.get("incident_confidence", 0.0)

    if confidence < confidence_threshold:
        logger.info(f"[Router] Low incident confidence ({confidence:.2%}), "
                   "routing to human_review")
        return "human_review"

    logger.debug(f"[Router] Incident confidence OK ({confidence:.2%}), "
                "routing to severity_classification")
    return "severity_classification"


def route_after_self_evaluation(
    state: EmergencyState
) -> Literal["flag_for_review", "complete_processing"]:
    """
    Route after self-evaluation node.

    If human review is required (low confidence or critical severity),
    route to flag_for_review. Otherwise, route to complete_processing.

    Args:
        state: Current EmergencyState after self-evaluation

    Returns:
        Next node name: "flag_for_review" or "complete_processing"
    """
    requires_review = state.get("requires_human_review", False)

    if requires_review:
        logger.info(f"[Router] Human review required, routing to flag_for_review. "
                   f"Concerns: {state.get('concerns', [])}")
        return "flag_for_review"

    logger.debug("[Router] No review required, routing to complete_processing")
    return "complete_processing"


def route_after_human_review(
    state: EmergencyState
) -> Literal["severity_classification", "end"]:
    """
    Route after human review node.

    After flagging for human review, continue with the pipeline
    to severity classification so we still generate predictions
    (which will be reviewed).

    Args:
        state: Current EmergencyState after human review node

    Returns:
        Next node name: "severity_classification" or "end"
    """
    # Continue to generate full predictions even when review is needed
    # This allows reviewers to see all AI predictions
    logger.debug("[Router] Continuing pipeline after human_review flag")
    return "severity_classification"


# =============================================================================
# Factory Functions for Configurable Routing
# =============================================================================

def create_incident_router(confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD):
    """
    Create an incident classification router with configurable threshold.

    Factory function that creates a router with a specific confidence
    threshold. Useful for integrating with config values.

    Args:
        confidence_threshold: Minimum confidence to continue without review

    Returns:
        Router function with threshold bound
    """
    def router(state: EmergencyState) -> Literal["severity_classification", "human_review"]:
        return route_after_incident_classification(state, confidence_threshold)

    return router


# =============================================================================
# Routing Constants
# =============================================================================

# Node names for routing
NODE_STT = "stt"
NODE_LANGUAGE_DETECTION = "language_detection"
NODE_INCIDENT_CLASSIFICATION = "incident_classification"
NODE_SEVERITY_CLASSIFICATION = "severity_classification"
NODE_DISPATCH_CLASSIFICATION = "dispatch_classification"
NODE_SELF_EVALUATION = "self_evaluation"
NODE_UNSUPPORTED_LANGUAGE = "unsupported_language_handler"
NODE_HUMAN_REVIEW = "human_review"
NODE_FLAG_FOR_REVIEW = "flag_for_review"
NODE_COMPLETE_PROCESSING = "complete_processing"
NODE_END = "end"


# Conditional edge mappings for clarity
LANGUAGE_DETECTION_ROUTES = {
    "incident_classification": NODE_INCIDENT_CLASSIFICATION,
    "unsupported_language_handler": NODE_UNSUPPORTED_LANGUAGE,
}

INCIDENT_CLASSIFICATION_ROUTES = {
    "severity_classification": NODE_SEVERITY_CLASSIFICATION,
    "human_review": NODE_HUMAN_REVIEW,
}

SELF_EVALUATION_ROUTES = {
    "flag_for_review": NODE_FLAG_FOR_REVIEW,
    "complete_processing": NODE_COMPLETE_PROCESSING,
}

HUMAN_REVIEW_ROUTES = {
    "severity_classification": NODE_SEVERITY_CLASSIFICATION,
    "end": NODE_END,
}
