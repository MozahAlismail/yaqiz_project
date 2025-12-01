"""
Language Detection Model Module

Handles automatic language detection from transcribed text.
Supports Arabic, English, and other languages.
"""

import logging
from typing import Dict, Any, List
import langdetect
from langdetect import detect_langs, detect
from collections import Counter

logger = logging.getLogger(__name__)


class LanguageDetectionModel:
    """
    Language detection model using langdetect library.
    
    Attributes:
        supported_languages: List of supported language codes
        confidence_threshold: Minimum confidence threshold for detection
    """
    
    def __init__(
        self,
        supported_languages: List[str] = None,
        confidence_threshold: float = 0.85
    ):
        """
        Initialize language detection model.
        
        Args:
            supported_languages: List of supported language codes (e.g., ['ar', 'en'])
            confidence_threshold: Minimum confidence for reliable detection
        """
        self.supported_languages = supported_languages or ['ar', 'en']
        self.confidence_threshold = confidence_threshold
        
        # Set seed for reproducibility
        langdetect.DetectorFactory.seed = 0
        
        logger.info(f"Language Detection initialized. Supported: {self.supported_languages}")
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing:
                - language: Detected language code
                - confidence: Detection confidence score
                - all_probabilities: List of all detected language probabilities
                - is_supported: Whether language is in supported list
        """
        if not text or len(text.strip()) < 3:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "all_probabilities": [],
                "is_supported": False,
                "error": "Text too short for detection"
            }
        
        try:
            # Detect language with probabilities
            lang_probs = detect_langs(text)
            
            # Get primary language
            primary_lang = lang_probs[0]
            detected_lang = primary_lang.lang
            confidence = primary_lang.prob
            
            # Format all probabilities
            all_probs = [
                {"language": lp.lang, "probability": lp.prob}
                for lp in lang_probs
            ]
            
            # Check if supported
            is_supported = detected_lang in self.supported_languages
            
            # Log detection
            logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.3f})")
            
            if confidence < self.confidence_threshold:
                logger.warning(f"Low confidence detection: {confidence:.3f}")
            
            if not is_supported:
                logger.warning(f"Unsupported language detected: {detected_lang}")
            
            return {
                "language": detected_lang,
                "confidence": confidence,
                "all_probabilities": all_probs,
                "is_supported": is_supported,
                "meets_threshold": confidence >= self.confidence_threshold
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "all_probabilities": [],
                "is_supported": False,
                "error": str(e)
            }
    
    def detect_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Detect language for multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of detection results
        """
        results = []
        for text in texts:
            result = self.detect_language(text)
            results.append(result)
        return results
    
    def get_dominant_language(self, texts: List[str]) -> Dict[str, Any]:
        """
        Get the most common language from multiple text samples.
        
        Args:
            texts: List of text samples
            
        Returns:
            Dictionary with dominant language info
        """
        detections = self.detect_batch(texts)
        
        # Count language occurrences
        languages = [d["language"] for d in detections if d["language"] != "unknown"]
        
        if not languages:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "is_supported": False
            }
        
        # Get most common
        lang_counts = Counter(languages)
        dominant_lang, count = lang_counts.most_common(1)[0]
        
        # Calculate average confidence for dominant language
        avg_confidence = sum(
            d["confidence"] for d in detections 
            if d["language"] == dominant_lang
        ) / count
        
        return {
            "language": dominant_lang,
            "confidence": avg_confidence,
            "occurrence_count": count,
            "total_samples": len(texts),
            "is_supported": dominant_lang in self.supported_languages
        }


def create_language_model(config: Dict[str, Any]) -> LanguageDetectionModel:
    """Factory function to create language detection model from config."""
    lang_config = config.get("models", {}).get("language_detection", {})
    
    return LanguageDetectionModel(
        supported_languages=lang_config.get("supported_languages", ["ar", "en"]),
        confidence_threshold=lang_config.get("confidence_threshold", 0.85)
    )
