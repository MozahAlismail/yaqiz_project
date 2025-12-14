"""
Streaming Emergency State Schema

Extends the base EmergencyState concept with streaming-specific fields for:
- Time-bounded confidence evaluation
- Processing metrics tracking
- Priority-based human review queue
- Unsupported language handling

IMPORTANT: This is a SEPARATE state type. It does NOT modify graph/state.py
"""

from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime


class ProcessingMetrics(TypedDict, total=False):
    """
    Track processing time for performance monitoring.
    All times in milliseconds. Timestamps as ISO strings.
    """
    # Timestamps
    chunk_received_at: str
    stt_started_at: str
    stt_completed_at: str
    graph_started_at: str
    language_detection_completed_at: str
    incident_classification_completed_at: str
    severity_classification_completed_at: str
    dispatch_classification_completed_at: str
    evaluation_completed_at: str
    response_sent_at: str

    # Durations (milliseconds)
    stt_time_ms: float
    language_detection_time_ms: float
    incident_classification_time_ms: float
    severity_classification_time_ms: float
    dispatch_classification_time_ms: float
    classification_total_time_ms: float
    evaluation_time_ms: float
    total_processing_time_ms: float

    # Chunk tracking
    chunks_processed: int

    # Flags
    classification_skipped: bool
    classification_skip_reason: str


class ConfidenceSnapshot(TypedDict):
    """Single confidence measurement at a point in time."""
    timestamp: str
    elapsed_seconds: float
    avg_confidence: float
    incident_confidence: float
    severity_confidence: float
    dispatch_confidence: float
    transcript_length: int


class StreamingEmergencyState(TypedDict, total=False):
    """
    Complete state schema for streaming emergency dispatch.

    ALL fields defined here - this is self-contained and does NOT
    depend on modifying the base EmergencyState.
    """

    # ===================================================================
    # INPUT FIELDS
    # ===================================================================
    audio_path: str                   # Empty for streaming
    case_id: str                      # Same as session_id

    # ===================================================================
    # SESSION MANAGEMENT
    # ===================================================================
    session_id: str                   # Unique WebSocket session ID
    is_streaming: bool                # Always True for streaming
    processing_mode: str              # "streaming"

    # ===================================================================
    # TRANSCRIPT FIELDS
    # ===================================================================
    transcript: str                   # Accumulated full transcript
    transcript_chunks: List[str]      # Individual chunks
    chunk_count: int                  # Number of chunks processed
    segments: List[dict]              # Transcript segments
    detected_language: str            # From Whisper
    language_probability: float       # From Whisper

    # ===================================================================
    # LANGUAGE VERIFICATION
    # ===================================================================
    language_confidence: float
    is_supported: bool
    unsupported_language_reason: str  # Clear reason for human if unsupported

    # ===================================================================
    # INCIDENT CLASSIFICATION
    # ===================================================================
    incident_type: str                # MEDICAL, FIRE, POLICE, etc.
    incident_confidence: float
    incident_reasoning: str
    keywords_found: List[str]

    # ===================================================================
    # SEVERITY CLASSIFICATION
    # ===================================================================
    severity_level: str               # CRITICAL, HIGH, MEDIUM, LOW
    severity_confidence: float
    severity_reasoning: str
    urgency_indicators: List[str]

    # ===================================================================
    # DISPATCH CLASSIFICATION
    # ===================================================================
    dispatch_unit: str                # POLICE, FIRE, AMBULANCE, etc.
    dispatch_confidence: float
    dispatch_reasoning: str
    estimated_priority: str           # Priority 1, 2, 3

    # ===================================================================
    # TIME-BOUNDED EVALUATION
    # ===================================================================
    evaluation_start_time: str        # ISO timestamp
    evaluation_window_seconds: float  # Default: 10.0
    elapsed_time_seconds: float
    confidence_threshold: float       # Default: 0.75
    confidence_history: List[ConfidenceSnapshot]
    confidence_threshold_met: bool
    window_expired: bool

    # ===================================================================
    # EXIT CONTROL
    # ===================================================================
    exit_reason: str                  # confidence_met, critical_severity, timeout,
                                      # unsupported_language, continue

    # ===================================================================
    # HUMAN REVIEW (ALL cases require review - no auto-dispatch)
    # ===================================================================
    requires_human_review: bool       # ALWAYS TRUE for completed cases
    review_priority: str              # "urgent", "high", "normal"
    overall_quality_score: float
    concerns: List[str]
    evaluation_summary: str
    low_confidence_areas: List[str]

    # ===================================================================
    # PROCESSING METRICS
    # ===================================================================
    processing_metrics: ProcessingMetrics

    # ===================================================================
    # METADATA
    # ===================================================================
    processing_status: str
    error: Optional[str]
    timestamps: dict


def create_streaming_initial_state(
    session_id: str,
    transcript: str = "",
    detected_language: str = "",
    confidence_threshold: float = 0.75,
    evaluation_window_seconds: float = 10.0
) -> StreamingEmergencyState:
    """
    Create initial state for a new streaming session.

    Args:
        session_id: Unique WebSocket session identifier
        transcript: Initial transcript (empty or first chunk)
        detected_language: Language detected by Whisper STT
        confidence_threshold: Confidence level to achieve (default: 0.75)
        evaluation_window_seconds: Max evaluation time (default: 10s)

    Returns:
        StreamingEmergencyState ready for graph invocation
    """
    now = datetime.utcnow().isoformat()

    return StreamingEmergencyState(
        # Session management
        session_id=session_id,
        is_streaming=True,
        processing_mode="streaming",
        case_id=session_id,
        audio_path="",

        # Time-bounded evaluation
        evaluation_start_time=now,
        evaluation_window_seconds=evaluation_window_seconds,
        elapsed_time_seconds=0.0,
        confidence_threshold=confidence_threshold,
        confidence_history=[],
        confidence_threshold_met=False,
        window_expired=False,

        # Exit control
        exit_reason="continue",

        # Transcript
        transcript=transcript,
        transcript_chunks=[transcript] if transcript else [],
        chunk_count=1 if transcript else 0,
        segments=[],
        detected_language=detected_language,
        language_probability=0.0,

        # Language verification (always supported - language forced via WebSocket param)
        language_confidence=1.0, #0.0
        is_supported=True,      #False
        unsupported_language_reason="",

        # Classification fields (initialized empty)
        incident_type="",
        incident_confidence=0.0,
        incident_reasoning="",
        keywords_found=[],

        severity_level="",
        severity_confidence=0.0,
        severity_reasoning="",
        urgency_indicators=[],

        dispatch_unit="",
        dispatch_confidence=0.0,
        dispatch_reasoning="",
        estimated_priority="",

        # Human review (always required)
        requires_human_review=False,  # Set to TRUE when case completes
        review_priority="normal",
        overall_quality_score=0.0,
        concerns=[],
        evaluation_summary="",
        low_confidence_areas=[],

        # Status
        processing_status="streaming_initialized",
        error=None,
        timestamps={
            "session_started": now,
            "evaluation_started": now
        },

        # Processing metrics
        processing_metrics=ProcessingMetrics(
            chunks_processed=0,
            total_processing_time_ms=0.0,
            classification_skipped=False,
            classification_skip_reason=""
        )
    )


# Punctuation marks to strip from intermediate chunks
# Includes: period, Arabic comma, Chinese period, exclamation, question marks
TRAILING_PUNCTUATION = ".。،,!?！？;；:："


def _strip_trailing_punctuation(text: str) -> str:
    """Remove trailing punctuation from text for cleaner concatenation."""
    return text.rstrip(TRAILING_PUNCTUATION).strip()


def _combine_chunks_intelligently(chunks: List[str]) -> str:
    """
    Combine transcript chunks into a coherent transcript.

    Removes trailing punctuation from all chunks except the last one,
    resulting in cleaner text for model classification.

    Example:
        ["Hello.", "World.", "End."] -> "Hello World End."
        ["شكراً.", "شكراً.", "في حريق."] -> "شكراً شكراً في حريق."
    """
    if not chunks:
        return ""

    if len(chunks) == 1:
        return chunks[0].strip()

    # Strip punctuation from all chunks except the last
    cleaned_parts = []
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if not chunk:
            continue

        if i < len(chunks) - 1:
            # Not the last chunk - remove trailing punctuation
            cleaned_parts.append(_strip_trailing_punctuation(chunk))
        else:
            # Last chunk - keep punctuation as-is
            cleaned_parts.append(chunk)

    return " ".join(cleaned_parts)


def update_streaming_state_with_transcript(
    state: StreamingEmergencyState,
    new_transcript_chunk: str,
    detected_language: str = None,
    chunk_received_at: str = None
) -> StreamingEmergencyState:
    """
    Update existing state with new transcript chunk.

    Combines chunks intelligently by removing trailing punctuation from
    previous chunks, resulting in a cleaner transcript for classification.

    Example flow:
        Chunk 1: "شكراً."   -> transcript: "شكراً."
        Chunk 2: "شكراً."   -> transcript: "شكراً شكراً."
        Chunk 3: "في حريق." -> transcript: "شكراً شكراً في حريق."

    Args:
        state: Existing streaming state
        new_transcript_chunk: New transcript text to append
        detected_language: Update language if provided
        chunk_received_at: Timestamp when chunk was received

    Returns:
        Updated state with accumulated transcript
    """
    chunks = list(state.get("transcript_chunks", []))
    chunks.append(new_transcript_chunk)

    # Combine chunks intelligently (strip punctuation from intermediate chunks)
    full_transcript = _combine_chunks_intelligently(chunks)

    start_time = datetime.fromisoformat(
        state.get("evaluation_start_time", datetime.utcnow().isoformat())
    )
    elapsed = (datetime.utcnow() - start_time).total_seconds()

    # Update metrics
    metrics = dict(state.get("processing_metrics", {}))
    metrics["chunks_processed"] = len(chunks)
    if chunk_received_at:
        metrics["chunk_received_at"] = chunk_received_at

    updated = dict(state)
    updated["transcript"] = full_transcript
    updated["transcript_chunks"] = chunks
    updated["chunk_count"] = len(chunks)
    updated["elapsed_time_seconds"] = elapsed
    updated["processing_metrics"] = metrics

    if detected_language:
        updated["detected_language"] = detected_language

    return StreamingEmergencyState(**updated)
