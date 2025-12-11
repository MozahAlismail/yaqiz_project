"""
LangGraph Node Functions for Emergency Dispatch Pipeline

Each node function receives the EmergencyState and returns a partial state dict
with updated values. Nodes preserve existing business logic from the original
agent implementations while adapting to the LangGraph pattern.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from graph.state import EmergencyState

# Global references to models/classifiers (set during initialization)
_stt_model = None
_language_model = None
_incident_classifier = None
_severity_classifier = None
_dispatch_classifier = None
_config = None


def init_nodes(
    stt_model,
    language_model,
    incident_classifier,
    severity_classifier,
    dispatch_classifier,
    config: dict
) -> None:
    """
    Initialize node dependencies with model/classifier instances.

    This function must be called during application startup to provide
    the nodes with access to the ML models and classifiers.

    Args:
        stt_model: STT model instance for transcription
        language_model: Language detection model instance
        incident_classifier: Incident classification model
        severity_classifier: Severity classification model
        dispatch_classifier: Dispatch classification model
        config: Application configuration dictionary
    """
    global _stt_model, _language_model, _incident_classifier
    global _severity_classifier, _dispatch_classifier, _config

    _stt_model = stt_model
    _language_model = language_model
    _incident_classifier = incident_classifier
    _severity_classifier = severity_classifier
    _dispatch_classifier = dispatch_classifier
    _config = config

    logger.info("LangGraph nodes initialized with models and classifiers")


def _update_timestamp(timestamps: dict, step: str) -> dict:
    """Update timestamps dict with current step completion time."""
    updated = dict(timestamps) if timestamps else {}
    updated[step] = datetime.utcnow().isoformat()
    return updated


# =============================================================================
# Main Pipeline Nodes
# =============================================================================

def stt_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Speech-to-Text node - Transcribes audio to text.

    Processes the audio file at state["audio_path"] and extracts:
    - Transcript text
    - Detected language
    - Language probability
    - Transcript segments with timestamps

    Args:
        state: Current EmergencyState

    Returns:
        Partial state dict with STT results or error
    """
    logger.info(f"[STT Node] Processing audio: {state.get('audio_path')}")

    try:
        if _stt_model is None:
            raise RuntimeError("STT model not initialized. Call init_nodes() first.")

        audio_path = state.get("audio_path")
        if not audio_path:
            raise ValueError("No audio_path provided in state")

        # Call the STT model transcribe method
        result = _stt_model.transcribe(audio_path)

        timestamps = _update_timestamp(state.get("timestamps", {}), "stt_completed")

        logger.info(f"[STT Node] Transcription complete. Language: {result.get('language')}")

        return {
            "transcript": result.get("text", ""),
            "segments": result.get("segments", []),
            "detected_language": result.get("language", "en"),
            "language_probability": result.get("language_probability", 0.0),
            "processing_status": "stt_complete",
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"[STT Node] Failed: {e}")
        return {
            "error": f"STT failed: {str(e)}",
            "processing_status": "failed",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "stt_failed")
        }


def language_detection_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Language Detection node - Verifies/detects transcript language.

    Uses the language detection model to verify the language detected
    by STT or detect language if STT didn't provide one.

    Args:
        state: Current EmergencyState with transcript

    Returns:
        Partial state dict with language verification results
    """
    logger.info("[Language Detection Node] Processing transcript")

    try:
        if _language_model is None:
            raise RuntimeError("Language model not initialized. Call init_nodes() first.")

        transcript = state.get("transcript", "")
        if not transcript:
            logger.warning("[Language Detection Node] Empty transcript")
            return {
                "language_confidence": 0.0,
                "is_supported": False,
                "processing_status": "language_detection_complete",
                "timestamps": _update_timestamp(state.get("timestamps", {}), "language_detection_completed")
            }

        # Call the language detection model
        result = _language_model.detect_language(transcript)

        detected_lang = result.get("language", "unknown")
        confidence = result.get("confidence", 0.0)
        is_supported = result.get("is_supported", False)

        # Override detected_language if language model has higher confidence
        stt_language = state.get("detected_language", "")
        final_language = detected_lang if confidence > state.get("language_probability", 0.0) else stt_language

        timestamps = _update_timestamp(state.get("timestamps", {}), "language_detection_completed")

        logger.info(f"[Language Detection Node] Language: {final_language}, Confidence: {confidence:.2%}")

        return {
            "detected_language": final_language,
            "language_confidence": confidence,
            "is_supported": is_supported,
            "processing_status": "language_detection_complete",
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"[Language Detection Node] Failed: {e}")
        # Don't fail the pipeline - use STT language as fallback
        return {
            "language_confidence": 0.0,
            "is_supported": False,
            "processing_status": "language_detection_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "language_detection_failed")
        }


def incident_classification_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Incident Classification node - Classifies the type of emergency.

    Uses the incident classifier to determine the type of emergency
    from the transcript (e.g., MEDICAL, FIRE, POLICE, etc.).

    Args:
        state: Current EmergencyState with transcript and language

    Returns:
        Partial state dict with incident classification results
    """
    logger.info("[Incident Classification Node] Classifying incident")

    try:
        if _incident_classifier is None:
            raise RuntimeError("Incident classifier not initialized. Call init_nodes() first.")

        transcript = state.get("transcript", "")
        language = state.get("detected_language", "en")

        # Call the incident classifier
        result = _incident_classifier.classify(transcript, language)

        timestamps = _update_timestamp(state.get("timestamps", {}), "incident_classification_completed")

        logger.info(f"[Incident Classification Node] Type: {result.get('incident_type')}, "
                   f"Confidence: {result.get('confidence', 0.0):.2%}")

        return {
            "incident_type": result.get("incident_type", "UNKNOWN"),
            "incident_confidence": result.get("confidence", 0.0),
            "incident_reasoning": result.get("reasoning", ""),
            "keywords_found": result.get("keywords_found", []),
            "processing_status": "incident_classification_complete",
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"[Incident Classification Node] Failed: {e}")
        return {
            "incident_type": "UNKNOWN",
            "incident_confidence": 0.0,
            "incident_reasoning": f"Classification failed: {str(e)}",
            "keywords_found": [],
            "processing_status": "incident_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "incident_classification_failed")
        }


def severity_classification_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Severity Classification node - Classifies the severity level.

    Uses the severity classifier to determine the severity of the
    incident (CRITICAL, HIGH, MEDIUM, LOW) based on transcript
    and incident type.

    Args:
        state: Current EmergencyState with transcript, language, and incident_type

    Returns:
        Partial state dict with severity classification results
    """
    logger.info("[Severity Classification Node] Classifying severity")

    try:
        if _severity_classifier is None:
            raise RuntimeError("Severity classifier not initialized. Call init_nodes() first.")

        transcript = state.get("transcript", "")
        incident_type = state.get("incident_type", "UNKNOWN")
        language = state.get("detected_language", "en")

        # Call the severity classifier
        result = _severity_classifier.classify(transcript, incident_type, language)

        timestamps = _update_timestamp(state.get("timestamps", {}), "severity_classification_completed")

        logger.info(f"[Severity Classification Node] Level: {result.get('severity_level')}, "
                   f"Confidence: {result.get('confidence', 0.0):.2%}")

        return {
            "severity_level": result.get("severity_level", "MEDIUM"),
            "severity_confidence": result.get("confidence", 0.0),
            "severity_reasoning": result.get("reasoning", ""),
            "urgency_indicators": result.get("urgency_indicators", []),
            "processing_status": "severity_classification_complete",
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"[Severity Classification Node] Failed: {e}")
        return {
            "severity_level": "MEDIUM",
            "severity_confidence": 0.0,
            "severity_reasoning": f"Classification failed: {str(e)}",
            "urgency_indicators": [],
            "processing_status": "severity_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "severity_classification_failed")
        }


def dispatch_classification_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Dispatch Classification node - Determines dispatch unit.

    Uses the dispatch classifier to determine which emergency unit
    should be dispatched based on transcript, incident type, and severity.

    Args:
        state: Current EmergencyState with transcript, language, incident_type, severity_level

    Returns:
        Partial state dict with dispatch classification results
    """
    logger.info("[Dispatch Classification Node] Determining dispatch unit")

    try:
        if _dispatch_classifier is None:
            raise RuntimeError("Dispatch classifier not initialized. Call init_nodes() first.")

        transcript = state.get("transcript", "")
        incident_type = state.get("incident_type", "UNKNOWN")
        severity_level = state.get("severity_level", "MEDIUM")
        language = state.get("detected_language", "en")

        # Call the dispatch classifier
        result = _dispatch_classifier.classify(transcript, incident_type, severity_level, language)

        timestamps = _update_timestamp(state.get("timestamps", {}), "dispatch_classification_completed")

        logger.info(f"[Dispatch Classification Node] Unit: {result.get('dispatch_unit')}, "
                   f"Priority: {result.get('estimated_priority')}")

        return {
            "dispatch_unit": result.get("dispatch_unit", "POLICE"),
            "dispatch_confidence": result.get("confidence", 0.0),
            "dispatch_reasoning": result.get("reasoning", ""),
            "estimated_priority": result.get("estimated_priority", "Priority 3"),
            "processing_status": "dispatch_classification_complete",
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"[Dispatch Classification Node] Failed: {e}")
        return {
            "dispatch_unit": "POLICE",
            "dispatch_confidence": 0.0,
            "dispatch_reasoning": f"Classification failed: {str(e)}",
            "estimated_priority": "Priority 3",
            "processing_status": "dispatch_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "dispatch_classification_failed")
        }


def self_evaluation_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Self-Evaluation node - Evaluates classification quality.

    Calculates overall quality score from classification confidences,
    identifies concerns, and determines if human review is required.

    Args:
        state: Current EmergencyState with all classification results

    Returns:
        Partial state dict with evaluation results
    """
    logger.info("[Self-Evaluation Node] Evaluating classification quality")

    try:
        # Get confidence threshold from config
        confidence_threshold = 0.75
        if _config:
            confidence_threshold = _config.get("hitl", {}).get("confidence_threshold", 0.75)

        # Get classification confidences
        incident_conf = state.get("incident_confidence", 0.0)
        severity_conf = state.get("severity_confidence", 0.0)
        dispatch_conf = state.get("dispatch_confidence", 0.0)

        # Calculate average confidence
        avg_confidence = (incident_conf + severity_conf + dispatch_conf) / 3.0

        # Determine if human review is needed
        requires_review = avg_confidence < confidence_threshold

        # Check for critical severity (always require review)
        if state.get("severity_level") == "CRITICAL":
            requires_review = True
            logger.info("[Self-Evaluation Node] CRITICAL severity - flagging for review")

        # Identify concerns
        concerns = []
        low_confidence_areas = []

        if incident_conf < 0.6:
            concerns.append("Low incident classification confidence")
            low_confidence_areas.append("incident")
        if severity_conf < 0.6:
            concerns.append("Low severity classification confidence")
            low_confidence_areas.append("severity")
        if dispatch_conf < 0.6:
            concerns.append("Low dispatch classification confidence")
            low_confidence_areas.append("dispatch")

        # Check for error in previous steps
        if state.get("error"):
            concerns.append(f"Pipeline error: {state.get('error')}")
            requires_review = True

        timestamps = _update_timestamp(state.get("timestamps", {}), "evaluation_completed")

        logger.info(f"[Self-Evaluation Node] Quality: {avg_confidence:.2%}, "
                   f"Review needed: {requires_review}")

        return {
            "overall_quality_score": avg_confidence,
            "requires_human_review": requires_review,
            "concerns": concerns,
            "evaluation_summary": f"Average confidence: {avg_confidence:.2%}",
            "low_confidence_areas": low_confidence_areas,
            "processing_status": "evaluation_complete",
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"[Self-Evaluation Node] Failed: {e}")
        # Fail-safe: require human review on any evaluation error
        return {
            "overall_quality_score": 0.0,
            "requires_human_review": True,
            "concerns": [f"Evaluation failed: {str(e)}"],
            "evaluation_summary": "Evaluation failed - manual review required",
            "low_confidence_areas": ["all"],
            "processing_status": "evaluation_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "evaluation_failed")
        }


# =============================================================================
# Handler Nodes for Conditional Routing
# =============================================================================

def unsupported_language_handler_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Handler for unsupported language cases.

    Called when the detected language is not in the supported languages list.
    Flags the case for manual handling and sets appropriate status.

    Args:
        state: Current EmergencyState

    Returns:
        Partial state dict with unsupported language handling
    """
    logger.warning(f"[Unsupported Language Handler] Language not supported: {state.get('detected_language')}")

    timestamps = _update_timestamp(state.get("timestamps", {}), "unsupported_language_handled")

    return {
        "requires_human_review": True,
        "concerns": [f"Unsupported language detected: {state.get('detected_language')}"],
        "processing_status": "unsupported_language",
        "error": f"Language '{state.get('detected_language')}' is not supported. Manual processing required.",
        "timestamps": timestamps
    }


def human_review_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Human Review node - Handles low-confidence classifications.

    Called when incident classification confidence is below threshold.
    Prepares the case for human review by a dispatcher.

    Args:
        state: Current EmergencyState

    Returns:
        Partial state dict with human review preparation
    """
    logger.info(f"[Human Review Node] Case flagged for review. Case ID: {state.get('case_id')}")

    concerns = list(state.get("concerns", []))
    concerns.append("Low incident confidence - requires human verification")

    timestamps = _update_timestamp(state.get("timestamps", {}), "human_review_flagged")

    return {
        "requires_human_review": True,
        "concerns": concerns,
        "processing_status": "pending_human_review",
        "timestamps": timestamps
    }


def flag_for_review_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Flag for Review node - Final review flagging after evaluation.

    Called when self-evaluation determines the case needs human review.
    This is the final node before END for cases requiring review.

    Args:
        state: Current EmergencyState

    Returns:
        Partial state dict with final review status
    """
    logger.info(f"[Flag for Review Node] Finalizing review flag. Case ID: {state.get('case_id')}")

    timestamps = _update_timestamp(state.get("timestamps", {}), "review_finalized")

    return {
        "processing_status": "flagged_for_review",
        "timestamps": timestamps
    }


def complete_processing_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Complete Processing node - Marks successful pipeline completion.

    Called when the pipeline completes successfully without requiring
    human review. Sets final status.

    Args:
        state: Current EmergencyState

    Returns:
        Partial state dict with completion status
    """
    logger.info(f"[Complete Processing Node] Pipeline completed. Case ID: {state.get('case_id')}")

    timestamps = _update_timestamp(state.get("timestamps", {}), "processing_completed")

    return {
        "processing_status": "completed",
        "timestamps": timestamps
    }
