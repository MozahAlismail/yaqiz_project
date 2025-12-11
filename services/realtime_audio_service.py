"""
realtime Audio Analysis Service

This service implements a hybrid workflow for processing audio files:
1. Uses faster-whisper (CTranslate2) for local speech-to-text
2. Optionally translates text using TranslationModel (MVS architecture)
3. Runs classification on the final text (translated or original)
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import os

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class realtimeAudioService:
    """Service for realtime audio analysis with hybrid STT and translation."""

    def __init__(
        self,
        whisper_model_size: str = "base",
        whisper_device: str = "cpu",
        whisper_compute_type: str = "int8",
        translation_model = None
    ):
        """
        Initialize the realtime audio service.

        Args:
            whisper_model_size: Size of the Whisper model (tiny, base, small, medium, large)
            whisper_device: Device to run Whisper on (cpu, cuda)
            whisper_compute_type: Compute type for CTranslate2 (int8, float16, float32)
            translation_model: TranslationModel instance for text translation
        """
        self.whisper_model = None
        self.whisper_model_size = whisper_model_size
        self.whisper_device = whisper_device
        self.whisper_compute_type = whisper_compute_type
        self.translation_model = translation_model

        logger.info("realtimeAudioService initialized")

    def _initialize_whisper_model(self):
        """Lazy initialization of Whisper model."""
        if self.whisper_model is None:
            logger.info(f"Loading Whisper model: {self.whisper_model_size}")
            logger.info(f"Device: {self.whisper_device}, Compute type: {self.whisper_compute_type}")

            # Initialize Whisper model with CTranslate2
            self.whisper_model = WhisperModel(
                self.whisper_model_size,
                device=self.whisper_device,
                compute_type=self.whisper_compute_type
            )
            logger.info("Whisper model loaded successfully")

    def transcribe_audio_file(self, audio_path: str) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Transcribe audio file using faster-whisper.

        This is a placeholder helper function name - integrate with your project's
        naming conventions.

        Args:
            audio_path: Path to the audio file

        Returns:
            Tuple of (full_transcript, detected_language, segments_list)
        """
        self._initialize_whisper_model()

        logger.info(f"Transcribing audio file: {audio_path}")

        # Process the audio file with faster-whisper
        # This automatically handles chunking internally
        segments, info = self.whisper_model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        detected_language = info.language
        logger.info(f"Detected language: {detected_language}")

        # Collect all segments
        all_segments = []
        full_transcript_parts = []

        for segment in segments:
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            all_segments.append(segment_data)
            full_transcript_parts.append(segment.text.strip())

        full_transcript = " ".join(full_transcript_parts)

        logger.info(f"Transcription complete. Total segments: {len(all_segments)}")

        return full_transcript, detected_language, all_segments

    def batch_transcript_segments(
        self,
        segments: List[Dict[str, Any]],
        batch_duration_seconds: float = 5.0
    ) -> List[str]:
        """
        Batch transcript segments for efficient processing.

        This is a placeholder helper function name - integrate with your project's
        naming conventions.

        Groups segments by time duration or sentence boundaries for batching.

        Args:
            segments: List of segment dictionaries with 'start', 'end', 'text'
            batch_duration_seconds: Duration in seconds to group segments

        Returns:
            List of batched text strings
        """
        if not segments:
            return []

        batches = []
        current_batch = []
        current_batch_start = segments[0]["start"]

        for segment in segments:
            # Check if we should start a new batch
            if segment["start"] - current_batch_start >= batch_duration_seconds:
                # Save current batch
                if current_batch:
                    batches.append(" ".join(current_batch))
                # Start new batch
                current_batch = [segment["text"]]
                current_batch_start = segment["start"]
            else:
                current_batch.append(segment["text"])

        # Add the last batch
        if current_batch:
            batches.append(" ".join(current_batch))

        logger.info(f"Created {len(batches)} batches from {len(segments)} segments")
        return batches

    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text using TranslationModel.

        Args:
            text: Text to translate
            target_language: Target language code or name (e.g., 'ar', 'Arabic')
            source_language: Source language (optional, for context)

        Returns:
            Translation result dictionary
        """
        if not self.translation_model:
            raise ValueError("Translation model not initialized.")

        logger.info(f"Translating text to {target_language}")

        # Use the translation model (MVS architecture)
        result = self.translation_model.translate(
            text=text,
            target_language=target_language,
            source_language=source_language
        )

        return result

    def process_audio_file(
        self,
        audio_path: str,
        translate: bool = True,
        target_language: str = "ar",
        incident_classifier = None,
        severity_classifier = None,
        dispatch_classifier = None
    ) -> Dict[str, Any]:
        """
        Process audio file through the complete hybrid workflow.

        This is a placeholder helper function name - integrate with your project's
        naming conventions.

        Workflow:
        1. Transcribe audio using faster-whisper
        2. Detect language
        3. Batch transcript segments (optional, for streaming scenarios)
        4. Translate if requested
        5. Select appropriate text for classification
        6. Run classification on final text (incident, severity, dispatch)

        Args:
            audio_path: Path to the audio file
            translate: Whether to translate the transcript
            target_language: Target language for translation
            incident_classifier: Existing incident classifier instance
            severity_classifier: Existing severity classifier instance
            dispatch_classifier: Existing dispatch classifier instance

        Returns:
            Complete analysis result dictionary
        """
        logger.info(f"Processing audio file: {audio_path}")

        # Step 1: Transcribe audio using faster-whisper
        full_transcript, detected_language, segments = self.transcribe_audio_file(audio_path)

        # Step 2: Batch transcript segments (for demonstration/logging)
        # In a streaming scenario, batching would be used for incremental processing
        batches = self.batch_transcript_segments(segments, batch_duration_seconds=5.0)
        logger.info(f"Transcript batched into {len(batches)} parts")

        # Step 3: Conditional translation
        translated_text = None
        translated_language = None

        if translate:
            logger.info("Translation requested")
            try:
                # Translate the full transcript using TranslationModel
                translation_result = self.translate_text(
                    full_transcript,
                    target_language,
                    source_language=detected_language
                )

                if translation_result["status"] == "success":
                    translated_text = translation_result["translated_text"]
                    translated_language = target_language
                else:
                    logger.error(f"Translation failed: {translation_result.get('error')}")
                    translate = False  # Fall back to original
            except Exception as e:
                logger.error(f"Translation failed, proceeding without translation: {e}")
                translate = False  # Fall back to original

        # Step 4: Select text and language for classification
        # IMPORTANT: Classification happens ONCE with the appropriate text and language
        # - If translate=True: Use translated_text with target_language rules
        # - If translate=False: Use original_transcript with detected_language rules

        if translate and translated_text:
            # Translation is enabled and successful
            text_for_classification = translated_text
            language_for_classification = target_language
            logger.info(f"Classification will use TRANSLATED text in '{target_language}' language")
            logger.info(f"Rules will be loaded from: config/emergency_rules/{target_language}/*_rules.json")
        else:
            # Translation disabled or failed - use original
            text_for_classification = full_transcript
            language_for_classification = detected_language
            logger.info(f"Classification will use ORIGINAL text in '{detected_language}' language")
            logger.info(f"Rules will be loaded from: config/emergency_rules/{detected_language}/*_rules.json")

        logger.info(f"Classification will happen ONCE using language: {language_for_classification}")
        logger.info(f"Classification results and reasoning will be in: {language_for_classification}")

        # Step 5: Run classification ONCE using the selected text and language
        # The classifiers will:
        # 1. Load rules from config/emergency_rules/{language_for_classification}/
        # 2. Use prompts configured for {language_for_classification}
        # 3. Return results and reasoning in {language_for_classification}
        classification_result = self._run_classification(
            text_for_classification,
            language_for_classification,
            incident_classifier,
            severity_classifier,
            dispatch_classifier
        )

        # Step 6: Compile final result
        result = {
            "original_transcript": full_transcript,
            "detected_language": detected_language,
            "translated_text": translated_text,  # None if translate=False
            "translated_language": translated_language,  # None if translate=False
            "classification": classification_result
        }

        logger.info("Audio processing completed successfully")
        return result

    def _run_classification(
        self,
        text: str,
        language: str,
        incident_classifier = None,
        severity_classifier = None,
        dispatch_classifier = None
    ) -> Dict[str, Any]:
        """
        Run classification ONCE on the provided text with specified language.

        Classification pipeline:
        1. Loads emergency rules from config/emergency_rules/{language}/
        2. Uses language-specific prompts
        3. Returns results and reasoning in the specified language

        Args:
            text: Text to classify (either translated or original)
            language: Language code (e.g., 'ar', 'en') - determines:
                      - Which rules to load (config/emergency_rules/{language}/)
                      - Language of classification results and reasoning
            incident_classifier: Existing incident classifier instance
            severity_classifier: Existing severity classifier instance
            dispatch_classifier: Existing dispatch classifier instance

        Returns:
            Classification results dictionary with reasoning in specified language
        """
        classification_result = {}

        logger.info(f"=== Starting Classification Pipeline (Language: {language}) ===")

        # Run incident classification if classifier provided
        if incident_classifier:
            try:
                logger.info(f"Running incident classification with language={language}")
                incident_result = incident_classifier.classify(text, language)
                classification_result["incident"] = incident_result
                logger.info(f"Incident classification complete: {incident_result.get('incident_type')}")
            except Exception as e:
                logger.error(f"Incident classification failed: {e}")
                classification_result["incident"] = {
                    "incident_type": "UNKNOWN",
                    "confidence": 0.0,
                    "error": str(e)
                }

        # Run severity classification if classifier provided
        if severity_classifier and "incident" in classification_result:
            try:
                incident_type = classification_result["incident"].get("incident_type", "UNKNOWN")
                logger.info(f"Running severity classification with language={language}, incident={incident_type}")
                severity_result = severity_classifier.classify(text, incident_type, language)
                classification_result["severity"] = severity_result
                logger.info(f"Severity classification complete: {severity_result.get('severity_level')}")
            except Exception as e:
                logger.error(f"Severity classification failed: {e}")
                classification_result["severity"] = {
                    "severity_level": "MEDIUM",
                    "confidence": 0.0,
                    "error": str(e)
                }

        # Run dispatch classification if classifier provided
        if dispatch_classifier and "incident" in classification_result and "severity" in classification_result:
            try:
                incident_type = classification_result["incident"].get("incident_type", "UNKNOWN")
                severity_level = classification_result["severity"].get("severity_level", "MEDIUM")
                logger.info(f"Running dispatch classification with language={language}, incident={incident_type}, severity={severity_level}")
                dispatch_result = dispatch_classifier.classify(text, incident_type, severity_level, language)
                classification_result["dispatch"] = dispatch_result
                logger.info(f"Dispatch classification complete: {dispatch_result.get('dispatch_unit')}")
            except Exception as e:
                logger.error(f"Dispatch classification failed: {e}")
                classification_result["dispatch"] = {
                    "dispatch_unit": "POLICE",
                    "confidence": 0.0,
                    "error": str(e)
                }

        logger.info(f"=== Classification Pipeline Complete (Language: {language}) ===")
        return classification_result


def create_realtime_audio_service(
    config: Optional[Dict[str, Any]] = None,
    translation_model = None
) -> realtimeAudioService:
    """
    Factory function to create realtimeAudioService instance.

    Args:
        config: Configuration dictionary (optional)
        translation_model: TranslationModel instance (optional)

    Returns:
        realtimeAudioService instance
    """
    if config is None:
        config = {}

    whisper_config = config.get("whisper", {})

    return realtimeAudioService(
        whisper_model_size=whisper_config.get("model_size", "base"),
        whisper_device=whisper_config.get("device", "cpu"),
        whisper_compute_type=whisper_config.get("compute_type", "int8"),
        translation_model=translation_model
    )
