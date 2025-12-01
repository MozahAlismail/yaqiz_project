"""Severity Classification Agent"""

import logging
from typing import Dict, Any
from models.severity_classifier import SeverityClassifier

logger = logging.getLogger(__name__)


class SeverityAgent:
    """Agent for classifying severity levels."""
    
    def __init__(self, classifier: SeverityClassifier):
        self.classifier = classifier
        logger.info("Severity Agent initialized")
    
    def process(self, transcript: str, incident_type: str, language: str = "en") -> Dict[str, Any]:
        """Classify severity level."""
        try:
            result = self.classifier.classify(transcript, incident_type, language)
            return {
                "status": "success",
                "severity_level": result.get("severity_level", "MEDIUM"),
                "confidence": result.get("confidence", 0.0),
                "reasoning": result.get("reasoning", ""),
                "urgency_indicators": result.get("urgency_indicators", [])
            }
        except Exception as e:
            logger.error(f"Severity classification failed: {e}")
            return {"status": "error", "severity_level": "MEDIUM", "error": str(e)}
