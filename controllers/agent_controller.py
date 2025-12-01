"""Agent Controller - Orchestrates all AI agents"""

import logging
from typing import Dict, Any
from agents.stt_agent import STTAgent
from agents.language_detection_agent import LanguageDetectionAgent
from agents.incident_agent import IncidentAgent
from agents.severity_agent import SeverityAgent
from agents.dispatch_agent import DispatchAgent
from agents.self_eval_agent import SelfEvaluationAgent

logger = logging.getLogger(__name__)


class AgentController:
    """Orchestrates the multi-agent pipeline for emergency dispatch."""
    
    def __init__(
        self,
        stt_agent: STTAgent,
        language_agent: LanguageDetectionAgent,
        incident_agent: IncidentAgent,
        severity_agent: SeverityAgent,
        dispatch_agent: DispatchAgent,
        self_eval_agent: SelfEvaluationAgent
    ):
        self.stt_agent = stt_agent
        self.language_agent = language_agent
        self.incident_agent = incident_agent
        self.severity_agent = severity_agent
        self.dispatch_agent = dispatch_agent
        self.self_eval_agent = self_eval_agent
        logger.info("Agent Controller initialized")
    
    def process_emergency_call(self, audio_path: str) -> Dict[str, Any]:
        """
        Process emergency call through the full agent pipeline.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Processing emergency call: {audio_path}")
        
        # Step 1: Speech-to-Text
        stt_result = self.stt_agent.process(audio_path)
        if stt_result["status"] != "success":
            return {"error": "STT failed", "details": stt_result}
        
        transcript = stt_result["transcript"]
        detected_language = stt_result.get("detected_language", "en")
        
        # Step 2: Language Detection (verify)
        lang_result = self.language_agent.process(transcript)
        if lang_result["status"] == "success":
            detected_language = lang_result["language"]
        
        # Step 3: Incident Classification
        incident_result = self.incident_agent.process(transcript, detected_language)
        
        # Step 4: Severity Classification
        severity_result = self.severity_agent.process(
            transcript,
            incident_result.get("incident_type", "UNKNOWN"),
            detected_language
        )
        
        # Step 5: Dispatch Classification
        dispatch_result = self.dispatch_agent.process(
            transcript,
            incident_result.get("incident_type", "UNKNOWN"),
            severity_result.get("severity_level", "MEDIUM"),
            detected_language
        )
        
        # Step 6: Self-Evaluation
        eval_result = self.self_eval_agent.process(
            transcript,
            incident_result,
            severity_result,
            dispatch_result
        )
        
        # Compile complete result
        complete_result = {
            "transcript": transcript,
            "detected_language": detected_language,
            "language_confidence": lang_result.get("confidence", 0.0),
            "incident_type": incident_result.get("incident_type"),
            "incident_confidence": incident_result.get("confidence", 0.0),
            "severity_level": severity_result.get("severity_level"),
            "severity_confidence": severity_result.get("confidence", 0.0),
            "dispatch_unit": dispatch_result.get("dispatch_unit"),
            "dispatch_confidence": dispatch_result.get("confidence", 0.0),
            "evaluation": eval_result,
            "requires_human_review": eval_result.get("requires_human_review", False),
            "processing_status": "completed"
        }
        
        logger.info("Emergency call processing completed")
        return complete_result
