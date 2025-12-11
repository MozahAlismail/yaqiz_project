"""
realtime Audio Analysis Router

Provides REST API endpoint for realtime audio analysis with hybrid workflow.
Follows MVC architecture with proper separation of concerns.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Dict, Any
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["realtime-audio"])


# ============================================
# Input Validation
# ============================================

def validate_audio_file(file: UploadFile) -> Dict[str, Any]:
    """
    Validate uploaded audio file.

    Args:
        file: Uploaded file

    Returns:
        Validation result dictionary

    Raises:
        HTTPException: If validation fails
    """
    # Check if file exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No audio file provided"
        )

    # Check file extension
    allowed_extensions = [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed formats: {', '.join(allowed_extensions)}"
        )

    return {
        "filename": file.filename,
        "extension": file_extension,
        "valid": True
    }


def validate_language_code(language_code: str) -> str:
    """
    Validate and normalize language code.

    Args:
        language_code: Language code or name

    Returns:
        Normalized language code
    """
    # Common language mappings
    language_map = {
        "arabic": "ar",
        "english": "en",
        "spanish": "es",
        "french": "fr",
        "german": "de",
        "chinese": "zh",
        "japanese": "ja",
        "korean": "ko",
        "russian": "ru",
        "portuguese": "pt",
        "italian": "it",
        "dutch": "nl",
        "polish": "pl",
        "turkish": "tr",
        "hindi": "hi",
        "urdu": "ur"
    }

    # Normalize to lowercase
    normalized = language_code.lower().strip()

    # Return mapped code or original
    return language_map.get(normalized, normalized)


# ============================================
# Endpoint
# ============================================

@router.post("/realtime-audio-analyze")
async def realtime_audio_analyze(
    audio: UploadFile = File(..., description="Audio file to analyze"),
    translate: bool = Form(True, description="Whether to translate the transcript"),
    target_language: str = Form("ar", description="Target language for translation (e.g., 'ar', 'en', 'es')")
) -> Dict[str, Any]:
    """
    Analyze audio file using hybrid workflow with local STT and optional translation.

    **Workflow:**
    1. Transcribe audio using faster-whisper (local, no external API)
    2. Detect language of the audio
    3. Optionally translate using TranslationModel (GPT-4o-mini)
    4. Select appropriate text for classification based on translation setting
    5. Run classification pipeline (incident, severity, dispatch)
    6. Return structured results with validation details

    **Args:**
    - **audio**: Uploaded audio file (WAV, MP3, FLAC, M4A, OGG, WebM)
    - **translate**: Whether to translate the transcript (default: true)
    - **target_language**: Target language for translation (default: "ar")

    **Returns:**
    - Complete analysis including transcript, translation (if enabled), and all classifications
    - Case ID for tracking
    - Confidence scores for all classifications
    - Human review flag based on confidence thresholds

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/realtime-audio-analyze" \\
         -F "audio=@emergency_call.wav" \\
         -F "translate=true" \\
         -F "target_language=ar"
    ```
    """
    logger.info(f"realtime audio analysis request received - File: {audio.filename}, Translate: {translate}, Target: {target_language}")

    # Input validation
    try:
        validation_result = validate_audio_file(audio)
        logger.info(f"File validation passed: {validation_result}")
    except HTTPException as e:
        logger.error(f"File validation failed: {e.detail}")
        raise

    # Validate and normalize target language
    target_language = validate_language_code(target_language)

    # Save uploaded file temporarily
    file_extension = validation_result["extension"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        content = await audio.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        # Get controller from app state
        from main import get_realtime_audio_controller

        controller = get_realtime_audio_controller()

        if not controller:
            raise HTTPException(
                status_code=500,
                detail="realtime audio controller not initialized. Please check server configuration."
            )

        # Analyze audio through controller (MVC architecture)
        result = controller.analyze_realtime_audio(
            audio_path=tmp_path,
            translate=translate,
            target_language=target_language
        )

        # Check for errors
        if result.get("status") == "failed" or "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Audio analysis failed")
            )

        # Add input validation info to response
        result["input_validation"] = {
            "filename": validation_result["filename"],
            "file_extension": validation_result["extension"],
            "translate_requested": translate,
            "target_language": target_language,
            "validated": True
        }

        logger.info(f"realtime audio analysis completed successfully - Case ID: {result.get('case_id')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"realtime audio analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio analysis failed: {str(e)}"
        )

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                logger.debug(f"Temp file cleaned up: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")
