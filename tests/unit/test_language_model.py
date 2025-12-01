"""Unit tests for Language Detection Model"""

import pytest
from models.language_model import LanguageDetectionModel


def test_detect_english():
    """Test English language detection."""
    model = LanguageDetectionModel()
    result = model.detect_language("Hello, this is an emergency. Please send help.")
    
    assert result["language"] == "en"
    assert result["confidence"] > 0.8
    assert result["is_supported"] is True


def test_detect_arabic():
    """Test Arabic language detection."""
    model = LanguageDetectionModel()
    result = model.detect_language("هذا حالة طوارئ. أرجو المساعدة.")
    
    assert result["language"] == "ar"
    assert result["is_supported"] is True


def test_short_text():
    """Test detection with short text."""
    model = LanguageDetectionModel()
    result = model.detect_language("Hi")
    
    assert result["language"] == "unknown"
