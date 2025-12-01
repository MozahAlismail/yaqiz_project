"""Integration tests for the full processing pipeline"""

import pytest
from unittest.mock import Mock
from controllers.agent_controller import AgentController
from agents.stt_agent import STTAgent
from agents.language_detection_agent import LanguageDetectionAgent
from agents.incident_agent import IncidentAgent
from agents.severity_agent import SeverityAgent
from agents.dispatch_agent import DispatchAgent
from agents.self_eval_agent import SelfEvaluationAgent


def create_mock_agents():
    """Create mock agents for testing."""
    # Mock STT Agent
    mock_stt = Mock(spec=STTAgent)
    mock_stt.process.return_value = {
        "status": "success",
        "transcript": "There is a fire in the building",
        "segments": [],
        "detected_language": "en",
        "language_probability": 0.95
    }
    
    # Mock Language Agent
    mock_lang = Mock(spec=LanguageDetectionAgent)
    mock_lang.process.return_value = {
        "status": "success",
        "language": "en",
        "confidence": 0.95,
        "is_supported": True
    }
    
    # Mock Incident Agent
    mock_incident = Mock(spec=IncidentAgent)
    mock_incident.process.return_value = {
        "status": "success",
        "incident_type": "FIRE",
        "confidence": 0.9,
        "reasoning": "Fire detected",
        "keywords_found": ["fire"]
    }
    
    # Mock Severity Agent
    mock_severity = Mock(spec=SeverityAgent)
    mock_severity.process.return_value = {
        "status": "success",
        "severity_level": "HIGH",
        "confidence": 0.88,
        "reasoning": "Building fire",
        "urgency_indicators": ["building", "fire"]
    }
    
    # Mock Dispatch Agent
    mock_dispatch = Mock(spec=DispatchAgent)
    mock_dispatch.process.return_value = {
        "status": "success",
        "dispatch_unit": "FIRE",
        "confidence": 0.92,
        "reasoning": "Fire department needed",
        "estimated_priority": "Priority 1"
    }
    
    # Mock Self-Eval Agent
    mock_eval = Mock(spec=SelfEvaluationAgent)
    mock_eval.process.return_value = {
        "status": "success",
        "overall_quality_score": 0.90,
        "requires_human_review": False,
        "concerns": [],
        "evaluation_summary": "High confidence"
    }
    
    return mock_stt, mock_lang, mock_incident, mock_severity, mock_dispatch, mock_eval


def test_full_pipeline():
    """Test the complete agent pipeline."""
    agents = create_mock_agents()
    controller = AgentController(*agents)
    
    result = controller.process_emergency_call("test_audio.wav")
    
    assert result["processing_status"] == "completed"
    assert result["incident_type"] == "FIRE"
    assert result["severity_level"] == "HIGH"
    assert result["dispatch_unit"] == "FIRE"
    assert result["requires_human_review"] is False


def test_pipeline_with_low_confidence():
    """Test pipeline with low confidence scores."""
    agents = create_mock_agents()
    
    # Modify incident agent to return low confidence
    agents[2].process.return_value["confidence"] = 0.5
    
    controller = AgentController(*agents)
    result = controller.process_emergency_call("test_audio.wav")
    
    # Should flag for human review due to low confidence
    assert "evaluation" in result
