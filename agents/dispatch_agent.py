"""Dispatch Unit Classification Agent"""

import logging
from typing import Dict, Any
from models.dispatch_classifier import DispatchClassifier

logger = logging.getLogger(__name__)


class DispatchAgent:
    """Agent for determining dispatch units."""
    
    def __init__(self, classifier: DispatchClassifier):
        self.classifier = classifier
        logger.info("Dispatch Agent initialized")
    
    def process(self, transcript: str, incident_type: str, severity_level: str, language: str = "en") -> Dict[str, Any]:
        """Determine appropriate dispatch units."""
        try:
            result = self.classifier.classify(transcript, incident_type, severity_level, language)
            return {
                "status": "success",
                "dispatch_unit": result.get("dispatch_unit", "POLICE"),
                "confidence": result.get("confidence", 0.0),
                "reasoning": result.get("reasoning", ""),
                "estimated_priority": result.get("estimated_priority", "Priority 3")
            }
        except Exception as e:
            logger.error(f"Dispatch classification failed: {e}")
            return {"status": "error", "dispatch_unit": "POLICE", "error": str(e)}
