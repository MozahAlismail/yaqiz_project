"""Audio Analysis Router"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import tempfile
import os

router = APIRouter(prefix="/api", tags=["audio"])


@router.post("/analyze-audio")
async def analyze_audio(
    audio_file: UploadFile = File(...),
    controller=None
) -> Dict[str, Any]:
    """
    Analyze emergency audio file.
    
    Args:
        audio_file: Uploaded audio file
        
    Returns:
        Complete analysis results
    """
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as tmp_file:
        content = await audio_file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Get controller from app state
        from main import get_main_controller
        controller = get_main_controller()
        
        # Analyze audio
        result = controller.analyze_audio(tmp_path)
        
        return result
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
