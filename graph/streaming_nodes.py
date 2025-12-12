"""
Streaming LangGraph Node Functions

Defines streaming-specific nodes:
- Wrapped classification nodes with timing metrics
- confidence_gate_node: Time-bounded evaluation
- unsupported_language_handler_node: Direct to human with clear reason
- streaming_complete_node: Finalize for human review queue

IMPORTANT: This file IMPORTS from graph/nodes.py but does NOT modify it.
"""

from datetime import datetime
from typing import Dict, Any, List
from loguru import logger

from graph.streaming_state import (
    StreamingEmergencyState,
    ConfidenceSnapshot,
    ProcessingMetrics
)

# Import existing nodes for reuse (NO MODIFICATION to original file)
from graph.nodes import (
    language_detection_node as _base_language_detection_node,
    incident_classification_node as _base_incident_classification_node,
    severity_classification_node as _base_severity_classification_node,
    dispatch_classification_node as _base_dispatch_classification_node,
    _update_timestamp
)


# ═══════════════════════════════════════════════════════════════════════════
# WRAPPED NODES WITH TIMING METRICS
# ═══════════════════════════════════════════════════════════════════════════

def streaming_language_detection_node(state: StreamingEmergencyState) -> Dict[str, Any]:
    """Language detection with timing metrics for streaming workflow."""
    start_time = datetime.utcnow()
    logger.info(f"[Streaming] Language detection started")

    # Call base node
    result = _base_language_detection_node(state)

    end_time = datetime.utcnow()
    duration_ms = (end_time - start_time).total_seconds() * 1000

    # Update metrics
    metrics = dict(state.get("processing_metrics", {}))
    metrics["language_detection_completed_at"] = end_time.isoformat()
    metrics["language_detection_time_ms"] = duration_ms
    result["processing_metrics"] = metrics

    logger.info(f"[Streaming] Language detection: {result.get('detected_language')} "
                f"(supported: {result.get('is_supported')}) in {duration_ms:.1f}ms")
    return result


def streaming_incident_classification_node(state: StreamingEmergencyState) -> Dict[str, Any]:
    """Incident classification with timing metrics for streaming workflow."""
    start_time = datetime.utcnow()
    logger.info(f"[Streaming] Incident classification started")

    # Call base node
    result = _base_incident_classification_node(state)

    end_time = datetime.utcnow()
    duration_ms = (end_time - start_time).total_seconds() * 1000

    # Update metrics
    metrics = dict(state.get("processing_metrics", {}))
    metrics["incident_classification_completed_at"] = end_time.isoformat()
    metrics["incident_classification_time_ms"] = duration_ms
    result["processing_metrics"] = metrics

    logger.info(f"[Streaming] Incident: {result.get('incident_type')} "
                f"({result.get('incident_confidence', 0):.2%}) in {duration_ms:.1f}ms")
    return result


def streaming_severity_classification_node(state: StreamingEmergencyState) -> Dict[str, Any]:
    """Severity classification with timing metrics for streaming workflow."""
    start_time = datetime.utcnow()
    logger.info(f"[Streaming] Severity classification started")

    # Call base node
    result = _base_severity_classification_node(state)

    end_time = datetime.utcnow()
    duration_ms = (end_time - start_time).total_seconds() * 1000

    # Update metrics
    metrics = dict(state.get("processing_metrics", {}))
    metrics["severity_classification_completed_at"] = end_time.isoformat()
    metrics["severity_classification_time_ms"] = duration_ms
    result["processing_metrics"] = metrics

    logger.info(f"[Streaming] Severity: {result.get('severity_level')} "
                f"({result.get('severity_confidence', 0):.2%}) in {duration_ms:.1f}ms")
    return result


def streaming_dispatch_classification_node(state: StreamingEmergencyState) -> Dict[str, Any]:
    """Dispatch classification with timing metrics for streaming workflow."""
    start_time = datetime.utcnow()
    logger.info(f"[Streaming] Dispatch classification started")

    # Call base node
    result = _base_dispatch_classification_node(state)

    end_time = datetime.utcnow()
    duration_ms = (end_time - start_time).total_seconds() * 1000

    # Update metrics
    metrics = dict(state.get("processing_metrics", {}))
    metrics["dispatch_classification_completed_at"] = end_time.isoformat()
    metrics["dispatch_classification_time_ms"] = duration_ms

    # Calculate total classification time
    lang_time = metrics.get("language_detection_time_ms", 0)
    incident_time = metrics.get("incident_classification_time_ms", 0)
    severity_time = metrics.get("severity_classification_time_ms", 0)
    metrics["classification_total_time_ms"] = lang_time + incident_time + severity_time + duration_ms

    result["processing_metrics"] = metrics

    logger.info(f"[Streaming] Dispatch: {result.get('dispatch_unit')} "
                f"({result.get('dispatch_confidence', 0):.2%}) in {duration_ms:.1f}ms")
    return result


# ═══════════════════════════════════════════════════════════════════════════
# UNSUPPORTED LANGUAGE HANDLER
# ═══════════════════════════════════════════════════════════════════════════

def streaming_unsupported_language_handler_node(state: StreamingEmergencyState) -> Dict[str, Any]:
    """
    Handler for unsupported language cases in streaming workflow.

    SKIPS all classification and goes directly to human review with:
    - URGENT priority
    - Clear reason message explaining why manual processing is needed
    - Original transcript preserved for human reference
    """
    detected_language = state.get("detected_language", "unknown")
    transcript = state.get("transcript", "")

    logger.warning("[Streaming Unsupported Language] ═══════════════════════════════════════")
    logger.warning(f"[Streaming Unsupported Language] LANGUAGE NOT SUPPORTED: {detected_language}")
    logger.warning(f"[Streaming Unsupported Language] Case requires MANUAL human processing")
    logger.warning("[Streaming Unsupported Language] ═══════════════════════════════════════")

    now = datetime.utcnow().isoformat()

    # Build clear reason message for human operator
    reason_message = (
        f"UNSUPPORTED LANGUAGE DETECTED\n"
        f"\n"
        f"Detected Language: {detected_language}\n"
        f"Supported Languages: Arabic (ar), English (en)\n"
        f"\n"
        f"AI CANNOT PROCESS THIS CALL\n"
        f"The emergency call is in a language not supported by the AI system.\n"
        f"\n"
        f"REQUIRED HUMAN ACTION:\n"
        f"1. Listen to the original audio recording\n"
        f"2. Manually translate/understand the caller's message\n"
        f"3. Manually classify: Incident Type, Severity, Dispatch Unit\n"
        f"4. Approve dispatch of appropriate emergency services\n"
        f"\n"
        f"Original transcript (may be inaccurate):\n"
        f"{transcript[:500]}{'...' if len(transcript) > 500 else ''}"
    )

    timestamps = dict(state.get("timestamps", {}))
    timestamps["unsupported_language_detected"] = now
    timestamps["forwarded_to_human"] = now

    # Update metrics
    metrics = dict(state.get("processing_metrics", {}))
    metrics["classification_skipped"] = True
    metrics["classification_skip_reason"] = "unsupported_language"

    return {
        # Exit information
        "exit_reason": "unsupported_language",
        "review_priority": "urgent",

        # Clear reason for human
        "unsupported_language_reason": reason_message,
        "concerns": [
            f"Unsupported language: {detected_language}",
            "AI classification skipped - manual processing required",
            "Human must listen to audio and manually classify"
        ],

        # Always requires review
        "requires_human_review": True,

        # Set classification fields to indicate manual processing needed
        "incident_type": "MANUAL_REVIEW_REQUIRED",
        "incident_confidence": 0.0,
        "incident_reasoning": f"Language '{detected_language}' not supported",

        "severity_level": "MANUAL_REVIEW_REQUIRED",
        "severity_confidence": 0.0,
        "severity_reasoning": f"Language '{detected_language}' not supported",

        "dispatch_unit": "MANUAL_REVIEW_REQUIRED",
        "dispatch_confidence": 0.0,
        "dispatch_reasoning": f"Language '{detected_language}' not supported",

        # Evaluation
        "overall_quality_score": 0.0,
        "evaluation_summary": f"UNSUPPORTED LANGUAGE ({detected_language}) - Manual processing required",
        "low_confidence_areas": ["incident", "severity", "dispatch"],

        # Status
        "processing_status": "unsupported_language_manual_required",

        # Metadata
        "timestamps": timestamps,
        "processing_metrics": metrics
    }


# ═══════════════════════════════════════════════════════════════════════════
# CONFIDENCE GATE NODE
# ═══════════════════════════════════════════════════════════════════════════

def confidence_gate_node(state: StreamingEmergencyState) -> Dict[str, Any]:
    """
    Confidence Gate Node - Time-bounded evaluation decision point.

    IMPORTANT: ALL completed cases require human review - NO auto-dispatch!
    This is an emergency system where human verification is MANDATORY.

    Exit Reasons (ALL go to human review, just different priorities):
    1. "critical_severity" -> URGENT priority (life-threatening)
    2. "timeout" -> HIGH priority (AI uncertain)
    3. "confidence_met" -> NORMAL priority (AI confident, still needs verification)
    4. "continue" -> Keep waiting for more audio data
    """
    eval_start = datetime.utcnow()

    logger.info("[Confidence Gate] ═══════════════════════════════════════")
    logger.info("[Confidence Gate] Evaluating confidence and time constraints")

    # Get configuration
    confidence_threshold = state.get("confidence_threshold", 0.75)
    window_seconds = state.get("evaluation_window_seconds", 10.0)

    # Get confidences
    incident_conf = state.get("incident_confidence", 0.0)
    severity_conf = state.get("severity_confidence", 0.0)
    dispatch_conf = state.get("dispatch_confidence", 0.0)
    avg_confidence = (incident_conf + severity_conf + dispatch_conf) / 3.0

    # Calculate elapsed time
    start_time_str = state.get("evaluation_start_time")
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        elapsed = (datetime.utcnow() - start_time).total_seconds()
    else:
        elapsed = 0.0

    severity_level = state.get("severity_level", "")

    # Track confidence history
    confidence_history = list(state.get("confidence_history", []))
    snapshot = ConfidenceSnapshot(
        timestamp=datetime.utcnow().isoformat(),
        elapsed_seconds=elapsed,
        avg_confidence=avg_confidence,
        incident_confidence=incident_conf,
        severity_confidence=severity_conf,
        dispatch_confidence=dispatch_conf,
        transcript_length=len(state.get("transcript", ""))
    )
    confidence_history.append(snapshot)

    # Log status
    logger.info(f"[Confidence Gate] Elapsed: {elapsed:.1f}s / {window_seconds}s")
    logger.info(f"[Confidence Gate] Avg Confidence: {avg_confidence:.2%} (threshold: {confidence_threshold:.2%})")
    logger.info(f"[Confidence Gate] Severity Level: {severity_level}")

    # ═══════════════════════════════════════════════════════════════
    # DECISION LOGIC - ALL cases require human review!
    # ═══════════════════════════════════════════════════════════════

    exit_reason = "continue"
    review_priority = "normal"
    concerns = list(state.get("concerns", []))

    # CHECK 1: CRITICAL severity -> URGENT priority review
    if severity_level == "CRITICAL" and severity_conf >= 0.6:
        exit_reason = "critical_severity"
        review_priority = "urgent"
        concerns.append("CRITICAL: Life-threatening emergency - requires immediate human verification")
        logger.warning(f"[Confidence Gate] CRITICAL SEVERITY - URGENT human review required!")

    # CHECK 2: Window expired with low confidence -> HIGH priority review
    elif elapsed >= window_seconds and avg_confidence < confidence_threshold:
        exit_reason = "timeout"
        review_priority = "high"
        concerns.append(f"LOW CONFIDENCE: AI uncertain ({avg_confidence:.2%}) - human review needed")
        logger.warning(f"[Confidence Gate] TIMEOUT with low confidence - HIGH priority review")

    # CHECK 3: Confidence threshold met -> NORMAL priority review
    elif avg_confidence >= confidence_threshold:
        exit_reason = "confidence_met"
        review_priority = "normal"
        logger.info(f"[Confidence Gate] CONFIDENCE MET at {elapsed:.1f}s - Normal priority review")

    # CHECK 4: Window expired but confidence is OK -> NORMAL priority review
    elif elapsed >= window_seconds:
        exit_reason = "confidence_met"
        review_priority = "normal"
        logger.info(f"[Confidence Gate] Window expired, confidence OK - Normal priority review")

    # CHECK 5: Continue waiting for more data
    else:
        exit_reason = "continue"
        remaining = window_seconds - elapsed
        logger.info(f"[Confidence Gate] CONTINUE - {remaining:.1f}s remaining")

    # ALL completed cases require human review
    requires_review = exit_reason != "continue"

    # Low confidence areas
    low_confidence_areas = []
    if incident_conf < 0.6:
        low_confidence_areas.append("incident")
    if severity_conf < 0.6:
        low_confidence_areas.append("severity")
    if dispatch_conf < 0.6:
        low_confidence_areas.append("dispatch")

    # Update metrics
    eval_end = datetime.utcnow()
    eval_duration_ms = (eval_end - eval_start).total_seconds() * 1000

    metrics = dict(state.get("processing_metrics", {}))
    metrics["evaluation_completed_at"] = eval_end.isoformat()
    metrics["evaluation_time_ms"] = eval_duration_ms

    # Calculate total processing time if final exit
    if exit_reason != "continue":
        chunk_received = metrics.get("chunk_received_at")
        if chunk_received:
            received_time = datetime.fromisoformat(chunk_received)
            total_ms = (eval_end - received_time).total_seconds() * 1000
            metrics["total_processing_time_ms"] = total_ms
            logger.info(f"[Confidence Gate] Total processing time: {total_ms:.1f}ms")

    timestamps = dict(state.get("timestamps", {}))
    timestamps["confidence_gate_evaluated"] = eval_end.isoformat()

    logger.info(f"[Confidence Gate] Decision: {exit_reason}, Priority: {review_priority}")
    logger.info("[Confidence Gate] ═══════════════════════════════════════")

    return {
        "exit_reason": exit_reason,
        "review_priority": review_priority,
        "requires_human_review": requires_review,
        "confidence_threshold_met": avg_confidence >= confidence_threshold,
        "window_expired": elapsed >= window_seconds,
        "elapsed_time_seconds": elapsed,
        "confidence_history": confidence_history,
        "overall_quality_score": avg_confidence,
        "concerns": concerns,
        "evaluation_summary": f"Confidence: {avg_confidence:.2%}, Elapsed: {elapsed:.1f}s, Exit: {exit_reason}",
        "low_confidence_areas": low_confidence_areas,
        "processing_metrics": metrics,
        "timestamps": timestamps
    }


# ═══════════════════════════════════════════════════════════════════════════
# STREAMING COMPLETE NODE
# ═══════════════════════════════════════════════════════════════════════════

def streaming_complete_node(state: StreamingEmergencyState) -> Dict[str, Any]:
    """
    Streaming Complete Node - Finalize case for human review queue.

    This node:
    1. Calculates final processing metrics
    2. Sets final review priority
    3. Prepares case for database save
    4. Ensures requires_human_review is TRUE (emergency system rule)
    """
    complete_time = datetime.utcnow()

    exit_reason = state.get("exit_reason", "unknown")
    review_priority = state.get("review_priority", "normal")

    logger.info("[Streaming Complete] ═══════════════════════════════════════")
    logger.info(f"[Streaming Complete] Exit Reason: {exit_reason}")
    logger.info(f"[Streaming Complete] Review Priority: {review_priority}")

    # Get current metrics
    metrics = dict(state.get("processing_metrics", {}))

    # Calculate final processing time
    graph_started = metrics.get("graph_started_at")
    if graph_started:
        start = datetime.fromisoformat(graph_started)
        total_ms = (complete_time - start).total_seconds() * 1000
        metrics["total_processing_time_ms"] = total_ms
        logger.info(f"[Streaming Complete] Total graph processing: {total_ms:.1f}ms")

    metrics["response_sent_at"] = complete_time.isoformat()

    # Update timestamps
    timestamps = dict(state.get("timestamps", {}))
    timestamps["streaming_completed"] = complete_time.isoformat()
    timestamps["ready_for_review"] = complete_time.isoformat()

    # Build evaluation summary
    avg_confidence = state.get("overall_quality_score", 0.0)
    incident_type = state.get("incident_type", "UNKNOWN")
    severity_level = state.get("severity_level", "UNKNOWN")
    dispatch_unit = state.get("dispatch_unit", "UNKNOWN")

    evaluation_summary = (
        f"Streaming analysis complete. "
        f"Exit: {exit_reason}. "
        f"Incident: {incident_type}, Severity: {severity_level}, Dispatch: {dispatch_unit}. "
        f"Avg Confidence: {avg_confidence:.2%}. "
        f"Priority: {review_priority.upper()}."
    )

    # Map priority to human-readable format
    priority_display = {
        "urgent": "URGENT - Immediate review required",
        "high": "HIGH - Priority review needed",
        "normal": "NORMAL - Standard review queue"
    }

    logger.info(f"[Streaming Complete] {priority_display.get(review_priority, review_priority)}")
    logger.info(f"[Streaming Complete] Case ready for human review")
    logger.info("[Streaming Complete] ═══════════════════════════════════════")

    return {
        # IMPORTANT: ALL cases require human review - no auto-dispatch!
        "requires_human_review": True,
        "review_priority": review_priority,
        "processing_status": "ready_for_review",
        "evaluation_summary": evaluation_summary,
        "processing_metrics": metrics,
        "timestamps": timestamps
    }