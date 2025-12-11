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
    
    def analyze_audio(self, audio_path: str, case_id: str = None) -> Dict[str, Any]:
        """
        Analyze emergency audio and store results.

        Uses the LangGraph workflow for processing.

        Args:
            audio_path: Path to audio file
            case_id: Optional case ID (auto-generated if not provided)

        Returns:
            Analysis results with case_id
        """
        try:
            # Generate case ID if not provided
            if not case_id:
                case_id = str(uuid.uuid4())

            # Process through LangGraph workflow
            result = self.agent_controller.process_emergency_call(audio_path, case_id)

            # Add case_id to result
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
        """
        Submit operator feedback for a case (UPSERT).

        If feedback already exists for this case_id, it will be updated.
        Otherwise, a new feedback record will be created.
        """
        try:
            case_id = feedback_data.get("case_id")

            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Check if feedback already exists for this case
            cursor.execute(
                "SELECT feedback_id FROM feedback WHERE case_id = %s",
                (case_id,)
            )
            existing = cursor.fetchone()

            if existing:
                # UPDATE existing feedback
                feedback_id = existing[0]

                cursor.execute("""
                    UPDATE feedback
                    SET corrected_incident = %s,
                        corrected_severity = %s,
                        corrected_unit = %s,
                        operator_id = %s,
                        timestamp = %s
                    WHERE case_id = %s
                """, (
                    feedback_data.get("corrected_incident"),
                    feedback_data.get("corrected_severity"),
                    feedback_data.get("corrected_unit"),
                    feedback_data.get("operator_id", "unknown"),
                    datetime.now(),
                    case_id
                ))

                conn.commit()
                cursor.close()
                conn.close()

                logger.info(f"Feedback {feedback_id} updated for case {case_id}")
                return {
                    "status": "success",
                    "feedback_id": feedback_id,
                    "action": "updated"
                }

            else:
                # INSERT new feedback
                feedback_id = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO feedback (
                        feedback_id, case_id, corrected_incident, corrected_severity,
                        corrected_unit, operator_id, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    feedback_id,
                    case_id,
                    feedback_data.get("corrected_incident"),
                    feedback_data.get("corrected_severity"),
                    feedback_data.get("corrected_unit"),
                    feedback_data.get("operator_id", "unknown"),
                    datetime.now()
                ))

                conn.commit()
                cursor.close()
                conn.close()

                logger.info(f"Feedback {feedback_id} created for case {case_id}")
                return {
                    "status": "success",
                    "feedback_id": feedback_id,
                    "action": "created"
                }

        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            return {"error": str(e)}

    def get_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """Retrieve feedback by ID."""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM feedback WHERE feedback_id = %s", (feedback_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return dict(row)
            return {"error": "Feedback not found"}

        except Exception as e:
            logger.error(f"Failed to retrieve feedback: {e}")
            return {"error": str(e)}

    def get_all_cases(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve all cases with pagination.

        Args:
            limit: Maximum number of cases to return (default: 100)
            offset: Number of cases to skip (default: 0)

        Returns:
            Dictionary with cases list and metadata
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM cases")
            total = cursor.fetchone()['total']

            # Get paginated cases
            cursor.execute("""
                SELECT * FROM cases
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))

            cases = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            logger.info(f"Retrieved {len(cases)} cases (limit: {limit}, offset: {offset})")

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "count": len(cases),
                "cases": cases
            }

        except Exception as e:
            logger.error(f"Failed to retrieve cases: {e}")
            return {"error": str(e)}

    def get_all_feedbacks(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve all feedbacks with pagination.

        Args:
            limit: Maximum number of feedbacks to return (default: 100)
            offset: Number of feedbacks to skip (default: 0)

        Returns:
            Dictionary with feedbacks list and metadata
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM feedback")
            total = cursor.fetchone()['total']

            # Get paginated feedbacks with case information
            cursor.execute("""
                SELECT
                    f.*,
                    c.transcript,
                    c.ai_incident,
                    c.ai_severity,
                    c.ai_unit
                FROM feedback f
                LEFT JOIN cases c ON f.case_id = c.case_id
                ORDER BY f.timestamp DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))

            feedbacks = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            logger.info(f"Retrieved {len(feedbacks)} feedbacks (limit: {limit}, offset: {offset})")

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "count": len(feedbacks),
                "feedbacks": feedbacks
            }

        except Exception as e:
            logger.error(f"Failed to retrieve feedbacks: {e}")
            return {"error": str(e)}

    def update_case(self, case_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update case information.

        Args:
            case_id: Case ID to update
            update_data: Dictionary with fields to update

        Returns:
            Success status and updated case data
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Check if case exists
            cursor.execute("SELECT case_id FROM cases WHERE case_id = %s", (case_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"error": "Case not found"}

            # Build UPDATE query dynamically for provided fields
            allowed_fields = {
                'transcript', 'detected_language', 'language_confidence',
                'ai_incident', 'ai_severity', 'ai_unit',
                'incident_confidence', 'severity_confidence', 'dispatch_confidence',
                'requires_review'
            }

            update_fields = []
            update_values = []

            for field, value in update_data.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)

            if not update_fields:
                cursor.close()
                conn.close()
                return {"error": "No valid fields to update"}

            update_values.append(case_id)

            query = f"""
                UPDATE cases
                SET {', '.join(update_fields)}
                WHERE case_id = %s
            """

            cursor.execute(query, update_values)
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Case {case_id} updated")
            return {"status": "success", "case_id": case_id, "updated_fields": list(update_data.keys())}

        except Exception as e:
            logger.error(f"Failed to update case: {e}")
            return {"error": str(e)}

    def update_feedback(self, feedback_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update feedback information.

        Args:
            feedback_id: Feedback ID to update
            update_data: Dictionary with fields to update

        Returns:
            Success status and updated feedback data
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Check if feedback exists
            cursor.execute("SELECT feedback_id FROM feedback WHERE feedback_id = %s", (feedback_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"error": "Feedback not found"}

            # Build UPDATE query dynamically for provided fields
            allowed_fields = {
                'corrected_incident', 'corrected_severity',
                'corrected_unit', 'operator_id'
            }

            update_fields = []
            update_values = []

            for field, value in update_data.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)

            if not update_fields:
                cursor.close()
                conn.close()
                return {"error": "No valid fields to update"}

            # Always update timestamp
            update_fields.append("timestamp = %s")
            update_values.append(datetime.now())
            update_values.append(feedback_id)

            query = f"""
                UPDATE feedback
                SET {', '.join(update_fields)}
                WHERE feedback_id = %s
            """

            cursor.execute(query, update_values)
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Feedback {feedback_id} updated")
            return {"status": "success", "feedback_id": feedback_id, "updated_fields": list(update_data.keys())}

        except Exception as e:
            logger.error(f"Failed to update feedback: {e}")
            return {"error": str(e)}

    def delete_case(self, case_id: str) -> Dict[str, Any]:
        """
        Delete a case by ID.

        Note: This will also delete associated feedback due to CASCADE constraint.

        Args:
            case_id: Case ID to delete

        Returns:
            Success status
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Check if case exists
            cursor.execute("SELECT case_id FROM cases WHERE case_id = %s", (case_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"error": "Case not found"}

            # Delete case (feedback will be deleted automatically due to CASCADE)
            cursor.execute("DELETE FROM cases WHERE case_id = %s", (case_id,))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Case {case_id} deleted (with associated feedback)")
            return {"status": "success", "case_id": case_id, "message": "Case and associated feedback deleted"}

        except Exception as e:
            logger.error(f"Failed to delete case: {e}")
            return {"error": str(e)}

    def delete_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """
        Delete a feedback by ID.

        Args:
            feedback_id: Feedback ID to delete

        Returns:
            Success status
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Check if feedback exists
            cursor.execute("SELECT feedback_id FROM feedback WHERE feedback_id = %s", (feedback_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"error": "Feedback not found"}

            # Delete feedback
            cursor.execute("DELETE FROM feedback WHERE feedback_id = %s", (feedback_id,))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Feedback {feedback_id} deleted")
            return {"status": "success", "feedback_id": feedback_id, "message": "Feedback deleted"}

        except Exception as e:
            logger.error(f"Failed to delete feedback: {e}")
            return {"error": str(e)}

    def get_analytics(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive analytics for dashboard.

        Returns:
            Dictionary containing:
            - feedback_analysis: edited vs correct cases with ratios
            - confidence_scores: average confidence scores
            - incident_types: distribution of incident types
            - languages: distribution of languages (en, ar, etc.)
            - severity_levels: distribution of severity levels
            - dispatch_units: distribution of dispatch units
        """
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # 1. Total cases
            cursor.execute("SELECT COUNT(*) as total FROM cases")
            total_cases = cursor.fetchone()['total']

            # 2. Feedback Analysis: Edited vs Correct cases
            # Check if feedback actually differs from AI predictions
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT CASE
                        WHEN f.case_id IS NOT NULL
                        AND (
                            f.corrected_incident != c.ai_incident
                            OR f.corrected_severity != c.ai_severity
                            OR f.corrected_unit != c.ai_unit
                        )
                        THEN c.case_id
                    END) as edited_cases,
                    COUNT(DISTINCT CASE
                        WHEN f.case_id IS NOT NULL
                        AND f.corrected_incident = c.ai_incident
                        AND f.corrected_severity = c.ai_severity
                        AND f.corrected_unit = c.ai_unit
                        THEN c.case_id
                    END) as operator_confirmed,
                    COUNT(DISTINCT CASE
                        WHEN f.case_id IS NULL
                        THEN c.case_id
                    END) as unreviewed_cases
                FROM cases c
                LEFT JOIN feedback f ON c.case_id = f.case_id
            """)
            feedback_stats = cursor.fetchone()
            edited_cases = feedback_stats['edited_cases'] or 0
            operator_confirmed = feedback_stats['operator_confirmed'] or 0
            unreviewed_cases = feedback_stats['unreviewed_cases'] or 0
            correct_cases = operator_confirmed + unreviewed_cases

            # 3. Average Confidence Scores
            cursor.execute("""
                SELECT
                    AVG(incident_confidence) as avg_incident,
                    AVG(severity_confidence) as avg_severity,
                    AVG(dispatch_confidence) as avg_dispatch,
                    COUNT(*) as total
                FROM cases
                WHERE incident_confidence IS NOT NULL
            """)
            confidence_stats = cursor.fetchone()

            # 4. Incident Types Distribution
            cursor.execute("""
                SELECT ai_incident, COUNT(*) as count
                FROM cases
                WHERE ai_incident IS NOT NULL
                GROUP BY ai_incident
                ORDER BY count DESC
            """)
            incident_rows = cursor.fetchall()
            incident_types = {}
            for row in incident_rows:
                incident_type = row['ai_incident']
                count = row['count']
                incident_types[incident_type] = {
                    "count": count,
                    "percentage": round((count / total_cases * 100) if total_cases > 0 else 0, 2)
                }

            # 5. Language Distribution
            cursor.execute("""
                SELECT detected_language, COUNT(*) as count
                FROM cases
                WHERE detected_language IS NOT NULL
                GROUP BY detected_language
                ORDER BY count DESC
            """)
            language_rows = cursor.fetchall()
            languages = {}
            for row in language_rows:
                lang = row['detected_language']
                count = row['count']
                languages[lang] = {
                    "count": count,
                    "percentage": round((count / total_cases * 100) if total_cases > 0 else 0, 2)
                }

            # 6. Severity Levels Distribution
            cursor.execute("""
                SELECT ai_severity, COUNT(*) as count
                FROM cases
                WHERE ai_severity IS NOT NULL
                GROUP BY ai_severity
                ORDER BY
                    CASE ai_severity
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                        ELSE 5
                    END
            """)
            severity_rows = cursor.fetchall()
            severity_levels = {}
            for row in severity_rows:
                severity = row['ai_severity']
                count = row['count']
                severity_levels[severity] = {
                    "count": count,
                    "percentage": round((count / total_cases * 100) if total_cases > 0 else 0, 2)
                }

            # 7. Dispatch Units Distribution
            cursor.execute("""
                SELECT ai_unit, COUNT(*) as count
                FROM cases
                WHERE ai_unit IS NOT NULL
                GROUP BY ai_unit
                ORDER BY count DESC
            """)
            dispatch_rows = cursor.fetchall()
            dispatch_units = {}
            for row in dispatch_rows:
                unit = row['ai_unit']
                count = row['count']
                dispatch_units[unit] = {
                    "count": count,
                    "percentage": round((count / total_cases * 100) if total_cases > 0 else 0, 2)
                }

            cursor.close()
            conn.close()

            # Build comprehensive analytics response
            analytics = {
                "total_cases": total_cases,
                "feedback_analysis": {
                    "total_cases": total_cases,
                    "edited_cases": edited_cases,
                    "correct_cases": correct_cases,
                    "operator_confirmed": operator_confirmed,
                    "unreviewed_cases": unreviewed_cases,
                    "edit_rate": round((edited_cases / total_cases) if total_cases > 0 else 0, 4),
                    "acceptance_rate": round((correct_cases / total_cases) if total_cases > 0 else 0, 4),
                    "review_rate": round(((edited_cases + operator_confirmed) / total_cases) if total_cases > 0 else 0, 4)
                },
                "confidence_scores": {
                    "incident": {
                        "average": round(float(confidence_stats['avg_incident'] or 0), 4),
                        "total_cases": confidence_stats['total']
                    },
                    "severity": {
                        "average": round(float(confidence_stats['avg_severity'] or 0), 4),
                        "total_cases": confidence_stats['total']
                    },
                    "dispatch": {
                        "average": round(float(confidence_stats['avg_dispatch'] or 0), 4),
                        "total_cases": confidence_stats['total']
                    }
                },
                "incident_types": incident_types,
                "languages": languages,
                "severity_levels": severity_levels,
                "dispatch_units": dispatch_units
            }

            logger.info("Analytics retrieved successfully")
            return analytics

        except Exception as e:
            logger.error(f"Failed to retrieve analytics: {e}")
            return {"error": str(e)}
