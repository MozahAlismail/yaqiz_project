"""realtime Audio Analysis Controller

Handles high-level orchestration for realtime audio analysis workflow.
Follows MVC architecture pattern.
"""

import logging
import uuid
from typing import Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class realtimeAudioController:
    """Controller for realtime audio analysis workflow."""

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
            incident_classifier: IncidentClassifier instance
            severity_classifier: SeverityClassifier instance
            dispatch_classifier: DispatchClassifier instance
            db_config: Database configuration dictionary
        """
        self.realtime_audio_service = realtime_audio_service
        self.incident_classifier = incident_classifier
        self.severity_classifier = severity_classifier
        self.dispatch_classifier = dispatch_classifier
        self.db_config = db_config
        logger.info("realtime Audio Controller initialized")

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
        Analyze realtime audio file through complete workflow.

        Args:
            audio_path: Path to audio file
            translate: Whether to translate the transcript
            target_language: Target language for translation

        Returns:
            Complete analysis results with case_id
        """
        try:
            logger.info(f"Processing realtime audio: translate={translate}, target_language={target_language}")

            # Process through service layer
            result = self.realtime_audio_service.process_audio_file(
                audio_path=audio_path,
                translate=translate,
                target_language=target_language,
                incident_classifier=self.incident_classifier,
                severity_classifier=self.severity_classifier,
                dispatch_classifier=self.dispatch_classifier
            )

            # Generate case ID
            case_id = str(uuid.uuid4())

            # Extract classification results
            classification = result.get("classification", {})
            incident_data = classification.get("incident", {})
            severity_data = classification.get("severity", {})
            dispatch_data = classification.get("dispatch", {})

            # Build response with all required fields
            response = {
                "case_id": case_id,
                "transcript": result.get("original_transcript", ""),
                "detected_language": result.get("detected_language", "unknown"),
                "language_confidence": 1.0,  # Faster-whisper provides high confidence
                "incident_type": incident_data.get("incident_type", "UNKNOWN"),
                "incident_confidence": incident_data.get("confidence", 0.0),
                "severity_level": severity_data.get("severity_level", "MEDIUM"),
                "severity_confidence": severity_data.get("confidence", 0.0),
                "dispatch_unit": dispatch_data.get("dispatch_unit", "POLICE"),
                "dispatch_confidence": dispatch_data.get("confidence", 0.0),
                "processing_status": "completed"
            }

            # Add translation fields if applicable
            if translate and result.get("translated_text"):
                response["translated_text"] = result.get("translated_text")
                response["translated_language"] = result.get("translated_language")
            else:
                response["translated_text"] = None
                response["translated_language"] = None

            # Add detailed classification results
            response["classification_details"] = {
                "incident": {
                    "type": incident_data.get("incident_type", "UNKNOWN"),
                    "confidence": incident_data.get("confidence", 0.0),
                    "reasoning": incident_data.get("reasoning", ""),
                    "keywords_found": incident_data.get("keywords_found", [])
                },
                "severity": {
                    "level": severity_data.get("severity_level", "MEDIUM"),
                    "confidence": severity_data.get("confidence", 0.0),
                    "reasoning": severity_data.get("reasoning", ""),
                    "urgency_indicators": severity_data.get("urgency_indicators", [])
                },
                "dispatch": {
                    "unit": dispatch_data.get("dispatch_unit", "POLICE"),
                    "confidence": dispatch_data.get("confidence", 0.0),
                    "reasoning": dispatch_data.get("reasoning", ""),
                    "estimated_priority": dispatch_data.get("estimated_priority", "Priority 3")
                }
            }

            # Determine if requires human review based on confidence scores
            avg_confidence = (
                response["incident_confidence"] +
                response["severity_confidence"] +
                response["dispatch_confidence"]
            ) / 3.0

            response["requires_human_review"] = avg_confidence < 0.75

            # Store in database
            self._store_realtime_audio_case(case_id, response)

            logger.info(f"realtime audio case {case_id} analyzed and stored")
            return response

        except Exception as e:
            logger.error(f"realtime audio analysis failed: {e}")
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
