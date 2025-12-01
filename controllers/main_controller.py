"""Main Controller - Handles high-level application logic"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from typing import Dict, Any
from datetime import datetime
from controllers.agent_controller import AgentController

logger = logging.getLogger(__name__)


class MainController:
    """Main controller for the Emergency Dispatch Assistant."""

    def __init__(self, agent_controller: AgentController, db_config: Dict[str, Any]):
        self.agent_controller = agent_controller
        self.db_config = db_config
        logger.info("Main Controller initialized")

    def _get_db_connection(self):
        """Get a PostgreSQL database connection."""
        return psycopg2.connect(
            host=self.db_config.get('host', 'localhost'),
            port=self.db_config.get('port', 5432),
            database=self.db_config.get('database', 'emergency_dispatch'),
            user=self.db_config.get('user', 'postgres'),
            password=self.db_config.get('password', 'postgres')
        )
    
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze emergency audio and store results.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Analysis results with case_id
        """
        try:
            # Process through agents
            result = self.agent_controller.process_emergency_call(audio_path)
            
            # Generate case ID
            case_id = str(uuid.uuid4())
            result["case_id"] = case_id
            
            # Store in database
            self._store_case(case_id, result)
            
            logger.info(f"Case {case_id} analyzed and stored")
            return result
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _store_case(self, case_id: str, result: Dict[str, Any]) -> None:
        """Store case in database."""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

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
                result.get("language_confidence", 0.0),
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
            logger.info(f"Case {case_id} stored in database")

        except Exception as e:
            logger.error(f"Failed to store case: {e}")
            raise
    
    def get_case(self, case_id: str) -> Dict[str, Any]:
        """Retrieve case by ID."""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM cases WHERE case_id = %s", (case_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return dict(row)
            return {"error": "Case not found"}

        except Exception as e:
            logger.error(f"Failed to retrieve case: {e}")
            return {"error": str(e)}
    
    def submit_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit operator feedback for a case."""
        try:
            feedback_id = str(uuid.uuid4())

            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO feedback (
                    feedback_id, case_id, corrected_incident, corrected_severity,
                    corrected_unit, operator_id, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                feedback_id,
                feedback_data.get("case_id"),
                feedback_data.get("corrected_incident"),
                feedback_data.get("corrected_severity"),
                feedback_data.get("corrected_unit"),
                feedback_data.get("operator_id", "unknown"),
                datetime.now()
            ))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Feedback {feedback_id} submitted for case {feedback_data.get('case_id')}")
            return {"status": "success", "feedback_id": feedback_id}

        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            return {"error": str(e)}
