"""WebSocket Audio Streaming Service

Handles real-time PCM audio streaming, buffering, transcription, and classification.
Follows the same architecture pattern as LiveAudioService.
"""

import logging
import io
import wave
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketAudioService:
    """Service for processing streaming PCM audio over WebSocket.

    PCM Audio Format:
        - Linear PCM
        - 16-bit signed
        - Mono channel
        - Sample rate: 16000 Hz (configurable)
        - Frame duration: 10-100 ms

    Workflow:
        1. Buffer incoming PCM frames
        2. Process chunks (0.5-2 sec) with Faster-Whisper for STT
        3. Optionally translate segments with GPT-4o-mini
        4. Update classification based on text_for_classification:
           - If translate=True: use translated_text
           - If translate=False: use original_transcript
        5. Stream partial results and final summary
    """

    def __init__(
        self,
        whisper_model_size: str,
        whisper_device: str,
        whisper_compute_type: str,
        translation_model,
        sample_rate: int = 16000,
        chunk_duration_seconds: float = 1.0,
        min_chunk_size_bytes: int = 16000  # ~0.5 sec at 16kHz mono 16-bit
    ):
        """Initialize WebSocket Audio Service.

        Args:
            whisper_model_size: Whisper model size (base, small, medium, large)
            whisper_device: Device to run Whisper (cpu, cuda)
            whisper_compute_type: Compute type (int8, float16, float32)
            translation_model: TranslationModel instance for optional translation
            sample_rate: PCM sample rate in Hz (default: 16000)
            chunk_duration_seconds: Target chunk duration for processing (default: 1.0)
            min_chunk_size_bytes: Minimum buffer size before processing (default: 16000 bytes)
        """
        self.whisper_model = None
        self.whisper_model_size = whisper_model_size
        self.whisper_device = whisper_device
        self.whisper_compute_type = whisper_compute_type
        self.translation_model = translation_model
        self.sample_rate = sample_rate
        self.chunk_duration_seconds = chunk_duration_seconds
        self.min_chunk_size_bytes = min_chunk_size_bytes

        logger.info(
            f"WebSocket Audio Service initialized: "
            f"sample_rate={sample_rate}Hz, "
            f"chunk_duration={chunk_duration_seconds}s"
        )

    def _load_whisper_model(self):
        """Lazy load Whisper model on first use."""
        if self.whisper_model is None:
            from faster_whisper import WhisperModel
            logger.info(f"Loading Whisper model: {self.whisper_model_size}")
            self.whisper_model = WhisperModel(
                self.whisper_model_size,
                device=self.whisper_device,
                compute_type=self.whisper_compute_type
            )
            logger.info("Whisper model loaded successfully")

    def create_session_state(self, translate: bool, target_language: str) -> Dict[str, Any]:
        """Create initial session state for WebSocket connection.

        Args:
            translate: Whether to translate transcripts
            target_language: Target language for translation (e.g., "ar", "en")

        Returns:
            Session state dictionary containing buffers and configuration
        """
        return {
            "translate": translate,
            "target_language": target_language,
            "audio_buffer": bytearray(),
            "original_transcript": "",
            "translated_text": "",
            "detected_language": None,
            "segment_count": 0,
            "total_audio_duration": 0.0,
            "started_at": datetime.now().isoformat()
        }

    def pcm_to_wav_bytes(self, pcm_data: bytes, sample_rate: int = 16000) -> bytes:
        """Convert raw PCM data to WAV format for Whisper processing.

        Args:
            pcm_data: Raw PCM audio bytes (16-bit signed, mono)
            sample_rate: Sample rate in Hz

        Returns:
            WAV formatted audio bytes
        """
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)

        wav_buffer.seek(0)
        return wav_buffer.read()

    def pcm_to_float32_array(self, pcm_data: bytes) -> np.ndarray:
        """Convert PCM bytes to float32 numpy array for Whisper.

        Args:
            pcm_data: Raw PCM audio bytes (16-bit signed, mono)

        Returns:
            Float32 numpy array normalized to [-1.0, 1.0]
        """
        # Convert bytes to int16 array
        audio_int16 = np.frombuffer(pcm_data, dtype=np.int16)

        # Convert to float32 and normalize to [-1.0, 1.0]
        audio_float32 = audio_int16.astype(np.float32) / 32768.0

        return audio_float32

    def transcribe_buffer(self, session_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transcribe audio buffer without classification (for streaming mode).

        This method only does STT - classification is handled by streaming LangGraph.

        Args:
            session_state: Current session state with audio buffer

        Returns:
            Dictionary with transcript text, language, and timing info
        """
        try:
            # Ensure Whisper model is loaded
            self._load_whisper_model()

            # Get audio data from buffer
            pcm_data = bytes(session_state["audio_buffer"])

            if len(pcm_data) < self.min_chunk_size_bytes:
                return None

            # Convert PCM to float32 array for Whisper
            audio_array = self.pcm_to_float32_array(pcm_data)

            # Calculate audio duration
            duration = len(pcm_data) / (self.sample_rate * 2)
            session_state["total_audio_duration"] += duration

            # Transcribe with Faster-Whisper
            stt_start = datetime.now()
            segments, info = self.whisper_model.transcribe(
                audio_array,
                beam_size=5,
                vad_filter=True,
                language=None  # Auto-detect
            )
            stt_time_ms = (datetime.now() - stt_start).total_seconds() * 1000

            # Extract detected language
            detected_language = info.language

            # Collect segment texts
            segment_texts = []
            for segment in segments:
                segment_texts.append(segment.text.strip())

            transcript_text = " ".join(segment_texts).strip()

            if not transcript_text:
                return None

            # Update session state
            if session_state["original_transcript"]:
                session_state["original_transcript"] += " " + transcript_text
            else:
                session_state["original_transcript"] = transcript_text

            if session_state["detected_language"] is None:
                session_state["detected_language"] = detected_language

            session_state["segment_count"] += 1

            return {
                "text": transcript_text,
                "full_transcript": session_state["original_transcript"],
                "detected_language": detected_language,
                "stt_time_ms": stt_time_ms,
                "audio_duration_seconds": duration,
                "segment_index": session_state["segment_count"]
            }

        except Exception as e:
            logger.error(f"Error transcribing buffer: {e}", exc_info=True)
            return None

    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Optional[str]:
        """Translate text using translation model.

        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (optional)

        Returns:
            Translated text or None if translation failed
        """
        if not self.translation_model:
            return None

        try:
            result = self.translation_model.translate(
                text=text,
                target_language=target_language,
                source_language=source_language
            )
            if result.get("status") == "success":
                return result.get("translated_text")
            return None
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return None

    def process_audio_chunk(
        self,
        session_state: Dict[str, Any],
        incident_classifier,
        severity_classifier,
        dispatch_classifier
    ) -> Optional[Dict[str, Any]]:
        """Process buffered audio chunk and generate partial result.

        This function:
        1. Transcribes the buffered audio chunk with Faster-Whisper
        2. Optionally translates the new segment
        3. Updates cumulative transcripts
        4. Runs classification on text_for_classification
        5. Returns partial result message

        Args:
            session_state: Current session state with audio buffer
            incident_classifier: IncidentClassifier instance
            severity_classifier: SeverityClassifier instance
            dispatch_classifier: DispatchClassifier instance

        Returns:
            Partial result dictionary or None if processing failed
        """
        try:
            # Ensure Whisper model is loaded
            self._load_whisper_model()

            # Get audio data from buffer
            pcm_data = bytes(session_state["audio_buffer"])

            if len(pcm_data) < self.min_chunk_size_bytes:
                logger.debug(f"Buffer too small: {len(pcm_data)} bytes, skipping processing")
                return None

            # Convert PCM to float32 array for Whisper
            audio_array = self.pcm_to_float32_array(pcm_data)

            # Calculate audio duration
            duration = len(pcm_data) / (self.sample_rate * 2)  # 2 bytes per sample
            session_state["total_audio_duration"] += duration

            # Transcribe with Faster-Whisper
            logger.info(f"Transcribing audio chunk: {duration:.2f}s")
            segments, info = self.whisper_model.transcribe(
                audio_array,
                beam_size=5,
                vad_filter=True,
                language=None  # Auto-detect
            )

            # Extract detected language (from first detection or previous state)
            if session_state["detected_language"] is None:
                session_state["detected_language"] = info.language
                logger.info(f"Detected language: {info.language}")

            # Collect segment texts
            segment_texts = []
            for segment in segments:
                segment_texts.append(segment.text.strip())

            new_transcript_segment = " ".join(segment_texts).strip()

            if not new_transcript_segment:
                logger.warning("No transcript generated from audio chunk")
                return None

            # Update original transcript
            if session_state["original_transcript"]:
                session_state["original_transcript"] += " " + new_transcript_segment
            else:
                session_state["original_transcript"] = new_transcript_segment

            # Handle translation if enabled
            if session_state["translate"]:
                # Translate the new segment
                translation_result = self.translation_model.translate(
                    text=new_transcript_segment,
                    target_language=session_state["target_language"],
                    source_language=session_state["detected_language"]
                )

                new_translated_segment = translation_result.get("translated_text", "")

                # Update cumulative translated text
                if session_state["translated_text"]:
                    session_state["translated_text"] += " " + new_translated_segment
                else:
                    session_state["translated_text"] = new_translated_segment

                # Set text for classification
                text_for_classification = session_state["translated_text"]
                language_for_classification = session_state["target_language"]
            else:
                # No translation - use original transcript
                text_for_classification = session_state["original_transcript"]
                language_for_classification = session_state["detected_language"]

            # Run classification on accumulated text
            classification_result = self._run_classification(
                text=text_for_classification,
                language=language_for_classification,
                incident_classifier=incident_classifier,
                severity_classifier=severity_classifier,
                dispatch_classifier=dispatch_classifier
            )

            # Increment segment count
            session_state["segment_count"] += 1

            # Build partial result with clear transcription section
            partial_result = {
                "type": "partial",
                "segment_index": session_state["segment_count"],
                "timestamp": datetime.now().isoformat(),
                "audio_duration_seconds": session_state["total_audio_duration"],

                # Transcription section - always includes both original and translated
                "transcription": {
                    "original_text": session_state["original_transcript"],
                    "original_language": session_state["detected_language"],
                    "translated_text": session_state["translated_text"] if session_state["translate"] else None,
                    "translated_language": session_state["target_language"] if session_state["translate"] else None,
                    "translation_enabled": session_state["translate"],
                    "text_used_for_classification": text_for_classification,
                    "classification_language": language_for_classification
                },

                # Legacy fields for backward compatibility
                "partial_transcript": session_state["original_transcript"],
                "detected_language": session_state["detected_language"],
                "partial_translated_text": session_state["translated_text"] if session_state["translate"] else None,
                "translated_language": session_state["target_language"] if session_state["translate"] else None,

                # Classification results
                "classification": classification_result
            }

            # Clear processed audio from buffer
            session_state["audio_buffer"].clear()

            logger.info(f"Partial result generated: segment {session_state['segment_count']}")
            return partial_result

        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}", exc_info=True)
            return None

    def generate_final_result(
        self,
        session_state: Dict[str, Any],
        incident_classifier,
        severity_classifier,
        dispatch_classifier
    ) -> Dict[str, Any]:
        """Generate final summary result for WebSocket session.

        Args:
            session_state: Current session state
            incident_classifier: IncidentClassifier instance
            severity_classifier: SeverityClassifier instance
            dispatch_classifier: DispatchClassifier instance

        Returns:
            Final result dictionary matching live_audio_analyze format
        """
        try:
            # Process any remaining audio in buffer
            if len(session_state["audio_buffer"]) >= self.min_chunk_size_bytes:
                logger.info("Processing remaining audio buffer for final result")
                self.process_audio_chunk(
                    session_state,
                    incident_classifier,
                    severity_classifier,
                    dispatch_classifier
                )

            # Determine text and language for final classification
            if session_state["translate"]:
                text_for_classification = session_state["translated_text"]
                language_for_classification = session_state["target_language"]
            else:
                text_for_classification = session_state["original_transcript"]
                language_for_classification = session_state["detected_language"] or "en"

            # Run final classification
            classification_result = self._run_classification(
                text=text_for_classification,
                language=language_for_classification,
                incident_classifier=incident_classifier,
                severity_classifier=severity_classifier,
                dispatch_classifier=dispatch_classifier
            )

            # Build final result with clear transcription section
            final_result = {
                "type": "final",
                "timestamp": datetime.now().isoformat(),
                "session_duration_seconds": session_state["total_audio_duration"],
                "total_segments": session_state["segment_count"],

                # Transcription section - always includes both original and translated
                "transcription": {
                    "original_text": session_state["original_transcript"],
                    "original_language": session_state["detected_language"] or "unknown",
                    "translated_text": session_state["translated_text"] if session_state["translate"] else None,
                    "translated_language": session_state["target_language"] if session_state["translate"] else None,
                    "translation_enabled": session_state["translate"],
                    "text_used_for_classification": text_for_classification,
                    "classification_language": language_for_classification
                },

                # Legacy fields for backward compatibility
                "original_transcript": session_state["original_transcript"],
                "detected_language": session_state["detected_language"] or "unknown",
                "translated_text": session_state["translated_text"] if session_state["translate"] else None,
                "translated_language": session_state["target_language"] if session_state["translate"] else None,

                # Classification results
                "classification": classification_result
            }

            logger.info(f"Final result generated: {session_state['segment_count']} segments processed")
            return final_result

        except Exception as e:
            logger.error(f"Error generating final result: {e}", exc_info=True)
            return {
                "type": "final",
                "error": str(e),
                "original_transcript": session_state["original_transcript"],
                "detected_language": session_state["detected_language"] or "unknown"
            }

    def _run_classification(
        self,
        text: str,
        language: str,
        incident_classifier,
        severity_classifier,
        dispatch_classifier
    ) -> Dict[str, Any]:
        """Run all three classifiers on the given text.

        Args:
            text: Text to classify (translated or original based on session config)
            language: Language of the text
            incident_classifier: IncidentClassifier instance
            severity_classifier: SeverityClassifier instance
            dispatch_classifier: DispatchClassifier instance

        Returns:
            Classification results dictionary
        """
        try:
            # Classify incident type
            incident_result = incident_classifier.classify(
                transcript=text,
                language=language
            )

            # Classify severity
            severity_result = severity_classifier.classify(
                transcript=text,
                incident_type=incident_result.get("incident_type", "UNKNOWN"),
                language=language
            )

            # Determine dispatch unit
            dispatch_result = dispatch_classifier.classify(
                transcript=text,
                incident_type=incident_result.get("incident_type", "UNKNOWN"),
                severity_level=severity_result.get("severity_level", "MEDIUM"),
                language=language
            )

            return {
                "incident": incident_result,
                "severity": severity_result,
                "dispatch": dispatch_result
            }

        except Exception as e:
            logger.error(f"Classification failed: {e}", exc_info=True)
            return {
                "incident": {
                    "incident_type": "UNKNOWN",
                    "confidence": 0.0,
                    "reasoning": str(e),
                    "keywords_found": []
                },
                "severity": {
                    "severity_level": "MEDIUM",
                    "confidence": 0.0,
                    "reasoning": str(e),
                    "urgency_indicators": []
                },
                "dispatch": {
                    "dispatch_unit": "POLICE",
                    "confidence": 0.0,
                    "reasoning": str(e),
                    "estimated_priority": "Priority 3"
                }
            }


def create_websocket_audio_service(config: Dict[str, Any], translation_model) -> WebSocketAudioService:
    """Factory function to create WebSocketAudioService from config.

    Args:
        config: Application configuration dictionary
        translation_model: TranslationModel instance

    Returns:
        WebSocketAudioService instance
    """
    whisper_config = config.get("whisper", {})

    return WebSocketAudioService(
        whisper_model_size=whisper_config.get("model_size", "base"),
        whisper_device=whisper_config.get("device", "cpu"),
        whisper_compute_type=whisper_config.get("compute_type", "int8"),
        translation_model=translation_model,
        sample_rate=whisper_config.get("sample_rate", 16000),
        chunk_duration_seconds=whisper_config.get("chunk_duration_seconds", 1.0),
        min_chunk_size_bytes=whisper_config.get("min_chunk_size_bytes", 16000)
    )
