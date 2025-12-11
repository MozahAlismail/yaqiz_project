"""Pytest configuration and fixtures"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture
def sample_transcript_en():
    """Sample English emergency transcript."""
    return "There is a fire in my house. Please send help immediately!"


@pytest.fixture
def sample_transcript_ar():
    """Sample Arabic emergency transcript."""
    return "يوجد حريق في منزلي. أرجو إرسال المساعدة فوراً!"


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "models": {
            "stt": {
                "model_name": "base",
                "device": "cpu",
                "compute_type": "int8"
            },
            "language_detection": {
                "supported_languages": ["ar", "en"],
                "confidence_threshold": 0.85
            },
            "llm": {
                "provider": "openai",
                "model_name": "gpt-4-turbo-preview",
                "temperature": 0.1,
                "max_tokens": 500
            }
        },
        "database": {
            "cases_db_path": "data/test_cases.db",
            "feedback_db_path": "data/test_feedback.db"
        },
        "hitl": {
            "confidence_threshold": 0.75
        }
    }
