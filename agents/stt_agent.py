"""STT Agent - Speech-to-Text Agent"""

import logging
from typing import Dict, Any
from models.stt_model import STTModel

logger = logging.getLogger(__name__)


class STTAgent:
    """Agent responsible for speech-to-text transcription."""
    
    def __init__(self, stt_model: STTModel):
        self.model = stt_model
        logger.info("STT Agent initialized")
    
    def process(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """Process audio file and return transcription."""
        try:
            result = self.model.transcribe(audio_path, language=language)
            return {
                "status": "success",
                "transcript": result["text"],
                "segments": result["segments"],
                "detected_language": result["language"],
                "language_probability": result["language_probability"]
            }
        except Exception as e:
            logger.error(f"STT Agent failed: {e}")
            return {"status": "error", "error": str(e)}
