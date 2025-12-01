"""Incident Classification Agent"""

import logging
from typing import Dict, Any
from models.incident_classifier import IncidentClassifier

logger = logging.getLogger(__name__)


class IncidentAgent:
    """Agent for classifying incident types."""
    
    def __init__(self, classifier: IncidentClassifier):
        self.classifier = classifier
        logger.info("Incident Agent initialized")
    
    def process(self, transcript: str, language: str = "en") -> Dict[str, Any]:
        """Classify incident type from transcript."""
        try:
            result = self.classifier.classify(transcript, language)
            return {
                "status": "success",
                "incident_type": result.get("incident_type", "UNKNOWN"),
                "confidence": result.get("confidence", 0.0),
                "reasoning": result.get("reasoning", ""),
                "keywords_found": result.get("keywords_found", [])
            }
        except Exception as e:
            logger.error(f"Incident classification failed: {e}")
            return {"status": "error", "incident_type": "UNKNOWN", "error": str(e)}
