"""Self-Evaluation Agent"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SelfEvaluationAgent:
    """Agent for evaluating AI classifications."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_threshold = config.get("hitl", {}).get("confidence_threshold", 0.75)
        logger.info("Self-Evaluation Agent initialized")
    
    def process(self, transcript: str, incident_result: Dict, severity_result: Dict, dispatch_result: Dict) -> Dict[str, Any]:
        """Evaluate the quality of classifications."""
        try:
            # Calculate average confidence
            avg_confidence = (
                incident_result.get("confidence", 0.0) +
                severity_result.get("confidence", 0.0) +
                dispatch_result.get("confidence", 0.0)
            ) / 3.0
            
            # Determine if human review is needed
            requires_review = avg_confidence < self.confidence_threshold
            
            # Check for critical severity (always require review)
            if severity_result.get("severity_level") == "CRITICAL":
                requires_review = True
            
            return {
                "status": "success",
                "overall_quality_score": avg_confidence,
                "requires_human_review": requires_review,
                "concerns": self._identify_concerns(incident_result, severity_result, dispatch_result),
                "evaluation_summary": f"Average confidence: {avg_confidence:.2%}"
            }
        except Exception as e:
            logger.error(f"Self-evaluation failed: {e}")
            return {"status": "error", "requires_human_review": True, "error": str(e)}
    
    def _identify_concerns(self, incident_result: Dict, severity_result: Dict, dispatch_result: Dict) -> list:
        """Identify any concerns in the classifications."""
        concerns = []
        if incident_result.get("confidence", 0.0) < 0.6:
            concerns.append("Low incident classification confidence")
        if severity_result.get("confidence", 0.0) < 0.6:
            concerns.append("Low severity classification confidence")
        if dispatch_result.get("confidence", 0.0) < 0.6:
            concerns.append("Low dispatch classification confidence")
        return concerns
