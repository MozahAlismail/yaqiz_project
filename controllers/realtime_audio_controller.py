"""realtime Audio Analysis Controller

Handles high-level orchestration for realtime audio analysis workflow.
Uses LangGraph workflow for classification (no STT node - STT handled by faster-whisper).
Follows MVC architecture pattern.
"""

import logging
import uuid
from typing import Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from graph.state import create_initial_state_from_transcript
from graph.workflow import get_emergency_graph

logger = logging.getLogger(__name__)


class realtimeAudioController:
    """Controller for realtime audio analysis workflow using LangGraph."""

    def __init__(
        self,
        realtime_audio_service,
        incident_classifier,
        severity_classifier,
        dispatch_classifier,
        db_config: Dict[str, Any]
    ):
        """
        Initialize realtime Audio Controller.

        Args:
            realtime_audio_service: realtimeAudioService instance
            incident_classifier: IncidentClassifier instance (for LangGraph nodes)
            severity_classifier: SeverityClassifier instance (for LangGraph nodes)
            dispatch_classifier: DispatchClassifier instance (for LangGraph nodes)
            db_config: Database configuration dictionary
        """
        self.realtime_audio_service = realtime_audio_service
        self.incident_classifier = incident_classifier
        self.severity_classifier = severity_classifier
        self.dispatch_classifier = dispatch_classifier
        self.db_config = db_config
        logger.info("realtime Audio Controller initialized (using LangGraph workflow)")

    def _get_db_connection(self):
        """Get a PostgreSQL database connection."""
        return psycopg2.connect(
            host=self.db_config.get('host', 'localhost'),
            port=self.db_config.get('port', 5432),
            database=self.db_config.get('database', 'emergency_dispatch'),
            user=self.db_config.get('user', 'postgres'),
            password=self.db_config.get('password', 'postgres')
        )

    def analyze_realtime_audio(
        self,
        audio_path: str,
        translate: bool = True,
        target_language: str = "ar"
    ) -> Dict[str, Any]:
        """
        Analyze realtime audio file through LangGraph workflow.

        Workflow:
        1. faster-whisper STT (in service layer)
        2. Optional translation (in service layer)
        3. LangGraph workflow: Language Detection → Incident → Severity → Dispatch → Evaluation

        Args:
            audio_path: Path to audio file
            translate: Whether to translate the transcript
            target_language: Target language for translation

        Returns:
            Complete analysis results with case_id
        """
        try:
            logger.info(f"Processing realtime audio: translate={translate}, target_language={target_language}")

            # Generate case ID
            case_id = str(uuid.uuid4())

            # Step 1: STT + optional translation through service layer
            stt_result = self.realtime_audio_service.transcribe_and_translate(
                audio_path=audio_path,
                translate=translate,
                target_language=target_language
            )

            original_transcript = stt_result.get("original_transcript", "")
            detected_language = stt_result.get("detected_language", "unknown")
            segments = stt_result.get("segments", [])
            translated_text = stt_result.get("translated_text")
            translated_language = stt_result.get("translated_language")

            # Step 2: Select text for classification
            # If translated, use translated text; otherwise use original
            if translate and translated_text:
                text_for_classification = translated_text
                classification_language = target_language
                logger.info(f"Using TRANSLATED text for LangGraph classification (lang={classification_language})")
            else:
                text_for_classification = original_transcript
                classification_language = detected_language
                logger.info(f"Using ORIGINAL text for LangGraph classification (lang={classification_language})")

            # Step 3: Create initial state and invoke LangGraph workflow
            initial_state = create_initial_state_from_transcript(
                transcript=text_for_classification,
                case_id=case_id,
                detected_language=classification_language,
                language_probability=0.95,  # faster-whisper provides high confidence
                segments=segments
            )

            # Get the compiled LangGraph (initialized in main.py)
            graph = get_emergency_graph()
            config = {"configurable": {"thread_id": case_id}}

            logger.info(f"Invoking LangGraph workflow for case {case_id}")
            start_time = datetime.now()
            result = graph.invoke(initial_state, config)
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"LangGraph workflow completed in {processing_time_ms:.1f}ms")

            # Step 4: Build response from LangGraph result
            response = {
                "case_id": case_id,
                "status": "success",

                # Transcript section - always includes both original and translated
                "transcription": {
                    "original_text": original_transcript,
                    "original_language": detected_language,
                    "translated_text": translated_text if translate and translated_text else None,
                    "translated_language": translated_language if translate and translated_text else None,
                    "translation_enabled": translate,
                    "text_used_for_classification": text_for_classification,
                    "classification_language": classification_language
                },

                # Legacy fields for backward compatibility
                "transcript": original_transcript,
                "detected_language": detected_language,
                "translated_text": translated_text if translate and translated_text else None,
                "translated_language": translated_language if translate and translated_text else None,

                # Classification results
                "language_confidence": result.get("language_confidence", 0.0),
                "incident_type": result.get("incident_type", "UNKNOWN"),
                "incident_confidence": result.get("incident_confidence", 0.0),
                "severity_level": result.get("severity_level", "MEDIUM"),
                "severity_confidence": result.get("severity_confidence", 0.0),
                "dispatch_unit": result.get("dispatch_unit", "POLICE"),
                "dispatch_confidence": result.get("dispatch_confidence", 0.0),
                "processing_status": result.get("processing_status", "completed"),
                "requires_human_review": result.get("requires_human_review", False),
                "overall_quality_score": result.get("overall_quality_score", 0.0)
            }

            # Add detailed classification results
            response["classification_details"] = {
                "incident": {
                    "type": result.get("incident_type", "UNKNOWN"),
                    "confidence": result.get("incident_confidence", 0.0),
                    "reasoning": result.get("incident_reasoning", ""),
                    "keywords_found": result.get("keywords_found", [])
                },
                "severity": {
                    "level": result.get("severity_level", "MEDIUM"),
                    "confidence": result.get("severity_confidence", 0.0),
                    "reasoning": result.get("severity_reasoning", ""),
                    "urgency_indicators": result.get("urgency_indicators", [])
                },
                "dispatch": {
                    "unit": result.get("dispatch_unit", "POLICE"),
                    "confidence": result.get("dispatch_confidence", 0.0),
                    "reasoning": result.get("dispatch_reasoning", ""),
                    "estimated_priority": result.get("estimated_priority", "Priority 3")
                }
            }

            # Add evaluation details
            response["evaluation"] = {
                "overall_confidence": result.get("overall_quality_score", 0.0),
                "requires_human_review": result.get("requires_human_review", False),
                "concerns": result.get("concerns", []),
                "summary": result.get("evaluation_summary", "")
            }

            # Add processing metrics
            response["processing_metrics"] = {
                "langgraph_time_ms": round(processing_time_ms, 1),
                "timestamps": result.get("timestamps", {})
            }

            # Store in database
            self._store_realtime_audio_case(case_id, response)

            logger.info(f"realtime audio case {case_id} analyzed and stored")
            return response

        except Exception as e:
            logger.error(f"realtime audio analysis failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "status": "failed",
                "processing_status": "failed"
            }

    def _store_realtime_audio_case(self, case_id: str, result: Dict[str, Any]) -> None:
        """
        Store realtime audio case in database.

        Args:
            case_id: Unique case identifier
            result: Analysis result dictionary
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Store in cases table (same structure as regular audio analysis)
            cursor.execute("""
                INSERT INTO cases (
                    case_id, transcript, detected_language, language_confidence,
                    ai_incident, ai_severity, ai_unit,
                    incident_confidence, severity_confidence, dispatch_confidence,
                    requires_review, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                case_id,
                result.get("transcript", ""),
                result.get("detected_language", "unknown"),
                result.get("language_confidence", 1.0),
                result.get("incident_type", "UNKNOWN"),
                result.get("severity_level", "MEDIUM"),
                result.get("dispatch_unit", "POLICE"),
                result.get("incident_confidence", 0.0),
                result.get("severity_confidence", 0.0),
                result.get("dispatch_confidence", 0.0),
                result.get("requires_human_review", False),
                datetime.now()
            ))

            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"realtime audio case {case_id} stored in database")

        except Exception as e:
            logger.error(f"Failed to store realtime audio case: {e}")
            raise
