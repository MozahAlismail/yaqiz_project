"""Language Detection Agent"""

import logging
from typing import Dict, Any
from models.language_model import LanguageDetectionModel

logger = logging.getLogger(__name__)


class LanguageDetectionAgent:
    """Agent for detecting language from transcript."""
    
    def __init__(self, model: LanguageDetectionModel):
        self.model = model
        logger.info("Language Detection Agent initialized")
    
    def process(self, transcript: str) -> Dict[str, Any]:
        """Detect language from transcript."""
        try:
            result = self.model.detect_language(transcript)
            return {
                "status": "success",
                "language": result["language"],
                "confidence": result["confidence"],
                "is_supported": result["is_supported"]
            }
        except Exception as e:
            logger.error(f"Language Detection failed: {e}")
            return {"status": "error", "language": "unknown", "error": str(e)}
