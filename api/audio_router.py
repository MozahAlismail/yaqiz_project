"""Audio Analysis Router

Provides REST API endpoint for audio analysis using LangGraph workflow.
Uses OpenAI Whisper API for STT (Speech-to-Text).

Endpoint: POST /api/analyze-audio
"""

import os
import tempfile
import logging
import uuid
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["audio"])

# Allowed audio file extensions
ALLOWED_EXTENSIONS = [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm", ".mp4"]


def validate_audio_file(file: UploadFile) -> Dict[str, Any]:
    """Validate uploaded audio file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    return {
        "filename": file.filename,
        "extension": file_extension,
        "valid": True
    }


@router.post("/analyze-audio")
async def analyze_audio(
    audio_file: UploadFile = File(..., description="Audio file to analyze"),
    language: str = Form("ar", description="Language code for transcription (default: ar)")
) -> Dict[str, Any]:
    """
    Analyze audio file using LangGraph workflow with OpenAI Whisper STT.

    **Workflow (LangGraph):**
    1. STT Node: Transcribe audio using OpenAI Whisper API
    2. Language Detection Node: Verify transcript language
    3. Incident Classification Node: Classify incident type
    4. Severity Classification Node: Classify severity level
    5. Dispatch Classification Node: Determine dispatch unit
    6. Evaluation Node: Calculate confidence and review flag

    **Args:**
    - **audio_file**: Audio file (WAV, MP3, FLAC, M4A, OGG, WebM)
    - **language**: Language code hint for transcription (default: "ar")

    **Returns:**
    - Complete analysis with transcript, classifications, and confidence scores

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/analyze-audio" \\
         -F "audio_file=@emergency_call.wav" \\
         -F "language=ar"
    ```
    """
    logger.info(f"Audio analysis request - File: {audio_file.filename}, Language: {language}")

    # Validate file
    try:
        validation = validate_audio_file(audio_file)
    except HTTPException:
        raise

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=validation["extension"]) as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Generate case ID
        case_id = str(uuid.uuid4())

        # Import and invoke the audio analysis LangGraph workflow
        from graph.audio_analysis_workflow import invoke_audio_analysis

        logger.info(f"Invoking audio analysis LangGraph workflow for case {case_id}")
        start_time = datetime.now()

        # Run the LangGraph workflow
        result = invoke_audio_analysis(tmp_path, case_id)

        total_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Check for errors
        if result.get("error"):
            logger.error(f"Audio analysis failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error"))

        # Store case in database
        try:
            from main import get_main_controller
            controller = get_main_controller()

            if controller:
                controller._store_case(case_id, {
                    "transcript": result.get("transcript", ""),
                    "detected_language": result.get("detected_language", "ar"),
                    "language_confidence": result.get("language_confidence", 0.0),
                    "incident_type": result.get("incident_type", "UNKNOWN"),
                    "incident_confidence": result.get("incident_confidence", 0.0),
                    "severity_level": result.get("severity_level", "MEDIUM"),
                    "severity_confidence": result.get("severity_confidence", 0.0),
                    "dispatch_unit": result.get("dispatch_unit", "POLICE"),
                    "dispatch_confidence": result.get("dispatch_confidence", 0.0),
                    "requires_human_review": result.get("requires_human_review", False)
                })
                logger.info(f"Case {case_id} stored in database")
        except Exception as db_error:
            logger.warning(f"Failed to store case in database: {db_error}")

        # Build response
        response = {
            "status": "success",
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "transcript": result.get("transcript", ""),
            "detected_language": result.get("detected_language", "ar"),
            "language_confidence": result.get("language_confidence", 0.0),
            "incident_type": result.get("incident_type", "UNKNOWN"),
            "incident_confidence": result.get("incident_confidence", 0.0),
            "incident_reasoning": result.get("incident_reasoning", ""),
            "keywords_found": result.get("keywords_found", []),
            "severity_level": result.get("severity_level", "MEDIUM"),
            "severity_confidence": result.get("severity_confidence", 0.0),
            "severity_reasoning": result.get("severity_reasoning", ""),
            "urgency_indicators": result.get("urgency_indicators", []),
            "dispatch_unit": result.get("dispatch_unit", "POLICE"),
            "dispatch_confidence": result.get("dispatch_confidence", 0.0),
            "dispatch_reasoning": result.get("dispatch_reasoning", ""),
            "estimated_priority": result.get("estimated_priority", "Priority 3"),
            "evaluation": {
                "overall_confidence": result.get("overall_quality_score", 0.0),
                "requires_human_review": result.get("requires_human_review", False),
                "concerns": result.get("concerns", []),
                "summary": result.get("evaluation_summary", "")
            },
            "processing_metrics": {
                "total_time_ms": round(total_time_ms, 1),
                "timestamps": result.get("timestamps", {})
            }
        }

        logger.info(f"Analysis complete - Case: {case_id}, "
                    f"Incident: {result.get('incident_type')}, "
                    f"Confidence: {result.get('overall_quality_score', 0):.2%}")

        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")


@router.get("/analyze-audio/info")
async def analyze_audio_info():
    """Get information about the analyze-audio endpoint."""
    return JSONResponse(content={
        "endpoint": "/api/analyze-audio",
        "method": "POST",
        "description": "Analyze audio file using LangGraph workflow with OpenAI Whisper STT",
        "workflow": {
            "nodes": [
                "1. STT Node - Transcribe audio using OpenAI Whisper API",
                "2. Language Detection Node - Verify transcript language",
                "3. Incident Classification Node - Classify incident type",
                "4. Severity Classification Node - Classify severity level",
                "5. Dispatch Classification Node - Determine dispatch unit",
                "6. Evaluation Node - Calculate confidence and review flag"
            ]
        },
        "parameters": {
            "audio_file": {
                "type": "file",
                "required": True,
                "description": "Audio file to analyze",
                "allowed_formats": ALLOWED_EXTENSIONS
            },
            "language": {
                "type": "string",
                "required": False,
                "default": "ar",
                "description": "Language code hint (ar, en, etc.)"
            }
        },
        "response": {
            "case_id": "Unique case identifier",
            "transcript": "Transcribed text from audio",
            "incident_type": "Classified incident type",
            "severity_level": "Severity level",
            "dispatch_unit": "Recommended dispatch unit",
            "evaluation": "Confidence scores and review status"
        },
        "example": {
            "curl": 'curl -X POST "http://localhost:8000/api/analyze-audio" -F "audio_file=@call.wav" -F "language=ar"'
        }
    })
