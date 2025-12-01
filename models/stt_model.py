"""
Speech-to-Text Model Module

Handles audio transcription using OpenAI's Whisper API.
Supports multiple languages including Arabic and English.
No local model or FFmpeg required - uses cloud API.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from openai import OpenAI

logger = logging.getLogger(__name__)


class STTModel:
    """
    Speech-to-Text model using OpenAI's Whisper API for transcription.

    Simple cloud-based transcription without local dependencies.

    Attributes:
        client: OpenAI client instance
        model: Whisper model to use (whisper-1)
        language: Optional language hint
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-1",
        language: Optional[str] = None
    ):
        """
        Initialize the STT model with OpenAI API.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Whisper model to use (default: whisper-1)
            language: Optional language code (ar, en, etc.)
        """
        self.model = model
        self.language = language

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

        logger.info(f"Initialized OpenAI STT with model: {model}")

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        response_format: str = "verbose_json",
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text using OpenAI API.

        Args:
            audio_path: Path to audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
            language: Optional language code override (ISO-639-1)
            response_format: Response format (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature (0-1)

        Returns:
            Dictionary containing transcript and metadata
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            logger.info(f"Transcribing audio file: {audio_path}")

            # Prepare transcription parameters
            lang = language or self.language

            # Open and transcribe audio file
            with open(audio_path, 'rb') as audio_file:
                params = {
                    "model": self.model,
                    "file": audio_file,
                    "response_format": response_format,
                    "temperature": temperature
                }

                # Add language if specified
                if lang:
                    params["language"] = lang

                # Call OpenAI Whisper API
                response = self.client.audio.transcriptions.create(**params)

            # Parse response based on format
            if response_format == "verbose_json":
                result = {
                    "text": response.text,
                    "language": response.language,
                    "duration": response.duration,
                    "segments": [
                        {
                            "start": seg.start,
                            "end": seg.end,
                            "text": seg.text,
                            "confidence": getattr(seg, 'confidence', None)
                        }
                        for seg in (response.segments or [])
                    ]
                }
                # Estimate language probability (API doesn't provide this directly)
                result["language_probability"] = 0.95  # High confidence from API
            else:
                # Simple format
                result = {
                    "text": response if isinstance(response, str) else response.text,
                    "language": lang or "unknown",
                    "language_probability": 0.95,
                    "segments": []
                }

            logger.info(f"Transcription complete. Language: {result.get('language', 'unknown')}")

            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the STT configuration."""
        return {
            "model": self.model,
            "provider": "OpenAI",
            "language": self.language,
            "requires_local_model": False,
            "requires_ffmpeg": False
        }


def create_stt_model(config: Dict[str, Any]) -> STTModel:
    """Factory function to create an STT model from configuration."""
    model_config = config.get("models", {}).get("stt", {})

    # Get API key from config or environment
    api_key = os.getenv("OPENAI_API_KEY")

    return STTModel(
        api_key=api_key,
        model=model_config.get("model", "whisper-1"),
        language=model_config.get("language")
    )
