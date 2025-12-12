"""
Audio Analysis LangGraph Workflow

Complete workflow for analyzing audio files:
1. STT (Speech-to-Text) using OpenAI Whisper API
2. Language Detection
3. Incident Classification
4. Severity Classification
5. Dispatch Classification
6. Self Evaluation

This is a separate graph from the streaming workflow.
Used for file upload analysis via POST /api/analyze-audio
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import EmergencyState, create_initial_state


# Global model references
_stt_model = None
_language_model = None
_incident_classifier = None
_severity_classifier = None
_dispatch_classifier = None
_config = None

# Global compiled graph
_audio_analysis_graph = None
_checkpointer = None


def init_audio_analysis_nodes(
    stt_model,
    language_model,
    incident_classifier,
    severity_classifier,
    dispatch_classifier,
    config: dict
) -> None:
    """Initialize audio analysis nodes with model dependencies."""
    global _stt_model, _language_model, _incident_classifier
    global _severity_classifier, _dispatch_classifier, _config

    _stt_model = stt_model
    _language_model = language_model
    _incident_classifier = incident_classifier
    _severity_classifier = severity_classifier
    _dispatch_classifier = dispatch_classifier
    _config = config

    logger.info("Audio analysis nodes initialized")


def _update_timestamp(timestamps: dict, step: str) -> dict:
    """Update timestamps dict with current step completion time."""
    updated = dict(timestamps) if timestamps else {}
    updated[step] = datetime.utcnow().isoformat()
    return updated


# =============================================================================
# STT Node - Speech to Text
# =============================================================================

def stt_node(state: EmergencyState) -> Dict[str, Any]:
    """
    Speech-to-Text node - Transcribes audio to text.

    Uses OpenAI Whisper API for transcription.

    Args:
        state: Current EmergencyState with audio_path

    Returns:
        Partial state dict with transcript and language info
    """
    logger.info("[STT Node] Transcribing audio")

    try:
        if _stt_model is None:
            raise RuntimeError("STT model not initialized")

        audio_path = state.get("audio_path", "")
        if not audio_path:
            raise ValueError("No audio path provided")

        # Transcribe using OpenAI Whisper API
        stt_start = datetime.utcnow()
        result = _stt_model.transcribe(audio_path, language="ar")
        stt_time = (datetime.utcnow() - stt_start).total_seconds() * 1000

        transcript = result.get("text", "").strip()
        detected_language = result.get("language", "ar")
        language_probability = result.get("language_probability", 0.95)
        segments = result.get("segments", [])

        logger.info(f"[STT Node] Transcribed: {len(transcript)} chars, "
                    f"lang={detected_language}, time={stt_time:.1f}ms")

        timestamps = _update_timestamp(state.get("timestamps", {}), "stt_completed")
        timestamps["stt_time_ms"] = stt_time

        return {
            "transcript": transcript,
            "segments": segments,
            "detected_language": detected_language,
            "language_probability": language_probability,
            "processing_status": "stt_complete",
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"[STT Node] Failed: {e}")
        return {
            "transcript": "",
            "detected_language": "ar",
            "language_probability": 0.0,
            "processing_status": "stt_failed",
            "error": str(e),
            "timestamps": _update_timestamp(state.get("timestamps", {}), "stt_failed")
        }


# =============================================================================
# Language Detection Node
# =============================================================================

def language_detection_node(state: EmergencyState) -> Dict[str, Any]:
    """Language Detection node - Verifies transcript language."""
    logger.info("[Language Detection Node] Processing")

    try:
        if _language_model is None:
            raise RuntimeError("Language model not initialized")

        transcript = state.get("transcript", "")
        if not transcript:
            return {
                "language_confidence": 0.0,
                "is_supported": False,
                "processing_status": "language_detection_complete",
                "timestamps": _update_timestamp(state.get("timestamps", {}), "language_detection_completed")
            }

        result = _language_model.detect_language(transcript)

        detected_lang = result.get("language", "unknown")
        confidence = result.get("confidence", 0.0)
        is_supported = result.get("is_supported", False)

        # Use detected language or fallback
        provided_language = state.get("detected_language", "ar")
        final_language = detected_lang if detected_lang != "unknown" else provided_language

        logger.info(f"[Language Detection Node] Language: {final_language}, Confidence: {confidence:.2%}")

        return {
            "detected_language": final_language,
            "language_confidence": confidence,
            "is_supported": is_supported,
            "processing_status": "language_detection_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "language_detection_completed")
        }

    except Exception as e:
        logger.error(f"[Language Detection Node] Failed: {e}")
        return {
            "language_confidence": 0.0,
            "is_supported": False,
            "processing_status": "language_detection_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "language_detection_failed")
        }


# =============================================================================
# Classification Nodes
# =============================================================================

def incident_classification_node(state: EmergencyState) -> Dict[str, Any]:
    """Incident Classification node."""
    logger.info("[Incident Classification Node] Classifying")

    try:
        if _incident_classifier is None:
            raise RuntimeError("Incident classifier not initialized")

        transcript = state.get("transcript", "")
        language = state.get("detected_language", "ar")

        # Use Arabic for classification rules
        classification_language = "ar"

        result = _incident_classifier.classify(
            transcript=transcript,
            language=classification_language
        )

        logger.info(f"[Incident Classification Node] Type: {result.get('incident_type')}, "
                    f"Confidence: {result.get('confidence', 0):.2%}")

        return {
            "incident_type": result.get("incident_type", "UNKNOWN"),
            "incident_confidence": result.get("confidence", 0.0),
            "incident_reasoning": result.get("reasoning", ""),
            "keywords_found": result.get("keywords_found", []),
            "processing_status": "incident_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "incident_classification_completed")
        }

    except Exception as e:
        logger.error(f"[Incident Classification Node] Failed: {e}")
        return {
            "incident_type": "UNKNOWN",
            "incident_confidence": 0.0,
            "incident_reasoning": str(e),
            "keywords_found": [],
            "processing_status": "incident_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "incident_classification_failed")
        }


def severity_classification_node(state: EmergencyState) -> Dict[str, Any]:
    """Severity Classification node."""
    logger.info("[Severity Classification Node] Classifying")

    try:
        if _severity_classifier is None:
            raise RuntimeError("Severity classifier not initialized")

        transcript = state.get("transcript", "")
        incident_type = state.get("incident_type", "UNKNOWN")
        classification_language = "ar"

        result = _severity_classifier.classify(
            transcript=transcript,
            incident_type=incident_type,
            language=classification_language
        )

        logger.info(f"[Severity Classification Node] Level: {result.get('severity_level')}, "
                    f"Confidence: {result.get('confidence', 0):.2%}")

        return {
            "severity_level": result.get("severity_level", "MEDIUM"),
            "severity_confidence": result.get("confidence", 0.0),
            "severity_reasoning": result.get("reasoning", ""),
            "urgency_indicators": result.get("urgency_indicators", []),
            "processing_status": "severity_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "severity_classification_completed")
        }

    except Exception as e:
        logger.error(f"[Severity Classification Node] Failed: {e}")
        return {
            "severity_level": "MEDIUM",
            "severity_confidence": 0.0,
            "severity_reasoning": str(e),
            "urgency_indicators": [],
            "processing_status": "severity_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "severity_classification_failed")
        }


def dispatch_classification_node(state: EmergencyState) -> Dict[str, Any]:
    """Dispatch Classification node."""
    logger.info("[Dispatch Classification Node] Classifying")

    try:
        if _dispatch_classifier is None:
            raise RuntimeError("Dispatch classifier not initialized")

        transcript = state.get("transcript", "")
        incident_type = state.get("incident_type", "UNKNOWN")
        severity_level = state.get("severity_level", "MEDIUM")
        classification_language = "ar"

        result = _dispatch_classifier.classify(
            transcript=transcript,
            incident_type=incident_type,
            severity_level=severity_level,
            language=classification_language
        )

        logger.info(f"[Dispatch Classification Node] Unit: {result.get('dispatch_unit')}, "
                    f"Confidence: {result.get('confidence', 0):.2%}")

        return {
            "dispatch_unit": result.get("dispatch_unit", "POLICE"),
            "dispatch_confidence": result.get("confidence", 0.0),
            "dispatch_reasoning": result.get("reasoning", ""),
            "estimated_priority": result.get("estimated_priority", "Priority 3"),
            "processing_status": "dispatch_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "dispatch_classification_completed")
        }

    except Exception as e:
        logger.error(f"[Dispatch Classification Node] Failed: {e}")
        return {
            "dispatch_unit": "POLICE",
            "dispatch_confidence": 0.0,
            "dispatch_reasoning": str(e),
            "estimated_priority": "Priority 3",
            "processing_status": "dispatch_classification_complete",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "dispatch_classification_failed")
        }


def evaluation_node(state: EmergencyState) -> Dict[str, Any]:
    """Self Evaluation node - calculates overall confidence and review flag."""
    logger.info("[Evaluation Node] Evaluating results")

    try:
        # Calculate average confidence
        incident_conf = state.get("incident_confidence", 0.0)
        severity_conf = state.get("severity_confidence", 0.0)
        dispatch_conf = state.get("dispatch_confidence", 0.0)

        avg_confidence = (incident_conf + severity_conf + dispatch_conf) / 3.0
        confidence_threshold = _config.get("hitl", {}).get("confidence_threshold", 0.75) if _config else 0.75

        requires_review = avg_confidence < confidence_threshold

        # Build concerns list
        concerns = []
        if incident_conf < confidence_threshold:
            concerns.append(f"Low incident confidence: {incident_conf:.2%}")
        if severity_conf < confidence_threshold:
            concerns.append(f"Low severity confidence: {severity_conf:.2%}")
        if dispatch_conf < confidence_threshold:
            concerns.append(f"Low dispatch confidence: {dispatch_conf:.2%}")

        logger.info(f"[Evaluation Node] Overall: {avg_confidence:.2%}, Review: {requires_review}")

        return {
            "overall_quality_score": avg_confidence,
            "requires_human_review": requires_review,
            "concerns": concerns,
            "evaluation_summary": f"Overall confidence: {avg_confidence:.2%}",
            "processing_status": "completed",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "evaluation_completed")
        }

    except Exception as e:
        logger.error(f"[Evaluation Node] Failed: {e}")
        return {
            "overall_quality_score": 0.0,
            "requires_human_review": True,
            "concerns": [str(e)],
            "evaluation_summary": "Evaluation failed",
            "processing_status": "completed",
            "timestamps": _update_timestamp(state.get("timestamps", {}), "evaluation_failed")
        }


# =============================================================================
# Edge Functions
# =============================================================================

def route_after_stt(state: EmergencyState) -> str:
    """Route after STT based on transcript presence."""
    transcript = state.get("transcript", "")
    if not transcript:
        return "end"
    return "language_detection"


# =============================================================================
# Graph Building
# =============================================================================

def build_audio_analysis_graph() -> StateGraph:
    """Build the audio analysis StateGraph."""
    logger.info("Building audio analysis graph")

    graph = StateGraph(EmergencyState)

    # Add nodes
    graph.add_node("stt", stt_node)
    graph.add_node("language_detection", language_detection_node)
    graph.add_node("incident_classification", incident_classification_node)
    graph.add_node("severity_classification", severity_classification_node)
    graph.add_node("dispatch_classification", dispatch_classification_node)
    graph.add_node("evaluation", evaluation_node)

    # Set entry point
    graph.set_entry_point("stt")

    # Add edges
    graph.add_conditional_edges(
        "stt",
        route_after_stt,
        {
            "language_detection": "language_detection",
            "end": END
        }
    )

    graph.add_edge("language_detection", "incident_classification")
    graph.add_edge("incident_classification", "severity_classification")
    graph.add_edge("severity_classification", "dispatch_classification")
    graph.add_edge("dispatch_classification", "evaluation")
    graph.add_edge("evaluation", END)

    logger.info("Audio analysis graph built")
    return graph


def create_audio_analysis_graph(
    stt_model,
    language_model,
    incident_classifier,
    severity_classifier,
    dispatch_classifier,
    config: dict,
    enable_checkpointing: bool = True
):
    """Create and compile the audio analysis graph."""
    global _audio_analysis_graph, _checkpointer

    # Initialize nodes
    init_audio_analysis_nodes(
        stt_model=stt_model,
        language_model=language_model,
        incident_classifier=incident_classifier,
        severity_classifier=severity_classifier,
        dispatch_classifier=dispatch_classifier,
        config=config
    )

    # Build graph
    graph = build_audio_analysis_graph()

    # Compile
    if enable_checkpointing:
        _checkpointer = MemorySaver()
        _audio_analysis_graph = graph.compile(checkpointer=_checkpointer)
        logger.info("Audio analysis graph compiled with checkpointing")
    else:
        _audio_analysis_graph = graph.compile()
        logger.info("Audio analysis graph compiled")

    return _audio_analysis_graph


def get_audio_analysis_graph():
    """Get the compiled audio analysis graph."""
    if _audio_analysis_graph is None:
        raise RuntimeError("Audio analysis graph not initialized")
    return _audio_analysis_graph


def invoke_audio_analysis(audio_path: str, case_id: str) -> EmergencyState:
    """
    Invoke audio analysis workflow.

    Args:
        audio_path: Path to audio file
        case_id: Unique case identifier

    Returns:
        Final EmergencyState after analysis
    """
    graph = get_audio_analysis_graph()
    initial_state = create_initial_state(audio_path, case_id)

    config = {"configurable": {"thread_id": case_id}}

    logger.info(f"Invoking audio analysis for case {case_id}")
    result = graph.invoke(initial_state, config)
    logger.info(f"Audio analysis completed for case {case_id}")

    return result
