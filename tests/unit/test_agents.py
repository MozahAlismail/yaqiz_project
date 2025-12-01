"""Unit tests for Agents"""

import pytest
from unittest.mock import Mock, MagicMock
from agents.stt_agent import STTAgent
from agents.language_detection_agent import LanguageDetectionAgent
from agents.incident_agent import IncidentAgent


def test_stt_agent_success():
    """Test STT Agent successful processing."""
    mock_model = Mock()
    mock_model.transcribe.return_value = {
        "text": "There is a fire",
        "segments": [],
        "language": "en",
        "language_probability": 0.95
    }
    
    agent = STTAgent(mock_model)
    result = agent.process("test.wav")
    
    assert result["status"] == "success"
    assert "transcript" in result


def test_language_agent():
    """Test Language Detection Agent."""
    mock_model = Mock()
    mock_model.detect_language.return_value = {
        "language": "en",
        "confidence": 0.9,
        "is_supported": True
    }
    
    agent = LanguageDetectionAgent(mock_model)
    result = agent.process("Test transcript")
    
    assert result["status"] == "success"
    assert result["language"] == "en"


def test_incident_agent():
    """Test Incident Classification Agent."""
    mock_classifier = Mock()
    mock_classifier.classify.return_value = {
        "incident_type": "FIRE",
        "confidence": 0.9,
        "reasoning": "Fire keywords detected",
        "keywords_found": ["fire"]
    }
    
    agent = IncidentAgent(mock_classifier)
    result = agent.process("There is a fire", "en")
    
    assert result["status"] == "success"
    assert result["incident_type"] == "FIRE"
