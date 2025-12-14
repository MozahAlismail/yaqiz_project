"""
Emergency Dispatch State Schema

Defines the EmergencyState TypedDict that represents the complete state
flowing through the LangGraph emergency dispatch workflow. All nodes
read from and write to this shared state.
"""

from typing import TypedDict, List, Optional, Any
from datetime import datetime


class EmergencyState(TypedDict, total=False):
    """
    Complete state schema for the emergency dispatch pipeline.

    This TypedDict defines all fields that flow through the LangGraph workflow.
    Each node reads relevant fields and returns a partial state dict with
    updated values. Using total=False allows partial state updates.

    Attributes:
        Input Fields:
            audio_path: Path to the audio file to process
            case_id: Unique identifier for this emergency case

        STT Output Fields:
            transcript: Transcribed text from audio
            segments: List of transcript segments with timestamps
            detected_language: Language code detected by STT (e.g., "en", "ar")
            language_probability: Confidence score from STT language detection

        Language Verification Fields:
            language_confidence: Confidence from language detection model
            is_supported: Whether the detected language is supported

        Incident Classification Fields:
            incident_type: Classified incident type (e.g., "MEDICAL", "FIRE", "POLICE")
            incident_confidence: Confidence score for incident classification
            incident_reasoning: Explanation of classification reasoning
            keywords_found: Keywords that triggered the classification

        Severity Classification Fields:
            severity_level: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
            severity_confidence: Confidence score for severity classification
            severity_reasoning: Explanation of severity assessment
            urgency_indicators: Indicators of urgency found in transcript

        Dispatch Classification Fields:
            dispatch_unit: Recommended dispatch unit (POLICE, FIRE, AMBULANCE, etc.)
            dispatch_confidence: Confidence score for dispatch classification
            dispatch_reasoning: Explanation of dispatch decision
            estimated_priority: Priority level (Priority 1, 2, or 3)

        Evaluation Fields:
            overall_quality_score: Average confidence across all classifications
            requires_human_review: Flag indicating HITL review is needed
            concerns: List of concerns identified during evaluation
            evaluation_summary: Summary text of the evaluation
            low_confidence_areas: Specific areas with low confidence scores

        Metadata Fields:
            processing_status: Current status of processing
            error: Error message if processing failed
            timestamps: Dict of timestamps for each processing step
    """

    # Input fields
    audio_path: str
    case_id: str

    # STT output fields
    transcript: str
    segments: List[dict]
    detected_language: str
    language_probability: float

    # Language verification fields
    language_confidence: float
    is_supported: bool

    # Incident classification fields
    incident_type: str
    incident_confidence: float
    incident_reasoning: str
    keywords_found: List[str]

    # Severity classification fields
    severity_level: str
    severity_confidence: float
    severity_reasoning: str
    urgency_indicators: List[str]

    # Dispatch classification fields
    dispatch_unit: str
    dispatch_confidence: float
    dispatch_reasoning: str
    estimated_priority: str

    # Evaluation fields
    overall_quality_score: float
    requires_human_review: bool
    concerns: List[str]
    evaluation_summary: str
    low_confidence_areas: List[str]

    # Metadata fields
    processing_status: str
    error: Optional[str]
    timestamps: dict


def create_initial_state(audio_path: str, case_id: str) -> EmergencyState:
    """
    Create an initial state for a new emergency dispatch workflow.

    Args:
        audio_path: Path to the audio file to process
        case_id: Unique identifier for this emergency case

    Returns:
        EmergencyState with input fields populated and defaults set
    """
    return EmergencyState(
        # Input
        audio_path=audio_path,
        case_id=case_id,

        # Initialize with empty/default values
        transcript="",
        segments=[],
        detected_language="",
        language_probability=0.0,

        language_confidence=0.0,
        is_supported=False,

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

        overall_quality_score=0.0,
        requires_human_review=False,
        concerns=[],
        evaluation_summary="",
        low_confidence_areas=[],

        processing_status="initialized",
        error=None,
        timestamps={
            "created": datetime.utcnow().isoformat()
        }
    )
