"""
Streaming Case Controller

Database operations for streaming emergency dispatch cases.
Handles case storage with processing metrics and review queue management.

IMPORTANT: ALL cases are saved with requires_review=TRUE.
This is an emergency system - NO auto-dispatch is allowed.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor, Json

logger = logging.getLogger(__name__)


class StreamingCaseController:
    """Controller for streaming case database operations.

    This controller handles:
    - Storing streaming cases with processing metrics
    - Managing the human review queue
    - Completing human reviews and saving feedback
    """

    def __init__(self, db_config: Dict[str, Any]):
        """Initialize the streaming case controller.

        Args:
            db_config: Database configuration dictionary
        """
        self.db_config = db_config
        logger.info("StreamingCaseController initialized")

    def _get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(
            host=self.db_config.get("host", "localhost"),
            port=self.db_config.get("port", 5432),
            database=self.db_config.get("database", "emergency_dispatch"),
            user=self.db_config.get("user", "postgres"),
            password=self.db_config.get("password", "")
        )

    def store_streaming_case(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Store a streaming case for human review.

        IMPORTANT: ALL cases have requires_review=TRUE.
        There is NO auto-dispatch in this emergency system.

        Args:
            state: StreamingEmergencyState dictionary

        Returns:
            Dictionary with success status, case_id, and review_priority
        """
        case_id = state.get("session_id") or state.get("case_id")
        exit_reason = state.get("exit_reason", "")
        review_priority = state.get("review_priority", "normal")
        metrics = state.get("processing_metrics", {})

        logger.info(f"[DB] Storing streaming case {case_id} "
                    f"(priority: {review_priority}, exit: {exit_reason})")

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Prepare JSON fields
            concerns = state.get("concerns", [])
            if isinstance(concerns, list):
                concerns_json = json.dumps(concerns)
            else:
                concerns_json = json.dumps([])

            metrics_json = json.dumps(metrics) if metrics else None

            cursor.execute("""
                INSERT INTO cases (
                    case_id, transcript, detected_language, language_confidence,
                    ai_incident, ai_severity, ai_unit,
                    incident_confidence, severity_confidence, dispatch_confidence,
                    requires_review, created_at,
                    processing_mode, total_processing_time_ms, stt_time_ms,
                    classification_time_ms, evaluation_time_ms, chunks_processed,
                    evaluation_window_seconds, exit_reason, review_priority,
                    unsupported_language_reason, evaluation_summary, concerns,
                    processing_metrics
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    TRUE, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (case_id) DO UPDATE SET
                    transcript = EXCLUDED.transcript,
                    ai_incident = EXCLUDED.ai_incident,
                    ai_severity = EXCLUDED.ai_severity,
                    ai_unit = EXCLUDED.ai_unit,
                    incident_confidence = EXCLUDED.incident_confidence,
                    severity_confidence = EXCLUDED.severity_confidence,
                    dispatch_confidence = EXCLUDED.dispatch_confidence,
                    requires_review = TRUE,
                    exit_reason = EXCLUDED.exit_reason,
                    review_priority = EXCLUDED.review_priority,
                    evaluation_summary = EXCLUDED.evaluation_summary,
                    concerns = EXCLUDED.concerns,
                    processing_metrics = EXCLUDED.processing_metrics,
                    total_processing_time_ms = EXCLUDED.total_processing_time_ms
            """, (
                case_id,
                state.get("transcript", ""),
                state.get("detected_language", "unknown"),
                state.get("language_confidence", 0.0),
                state.get("incident_type", "UNKNOWN"),
                state.get("severity_level", "MEDIUM"),
                state.get("dispatch_unit", "POLICE"),
                state.get("incident_confidence", 0.0),
                state.get("severity_confidence", 0.0),
                state.get("dispatch_confidence", 0.0),
                datetime.utcnow(),
                "streaming",
                metrics.get("total_processing_time_ms", 0.0),
                metrics.get("stt_time_ms", 0.0),
                metrics.get("classification_total_time_ms", 0.0),
                metrics.get("evaluation_time_ms", 0.0),
                metrics.get("chunks_processed", 0),
                state.get("evaluation_window_seconds", 10.0),
                exit_reason,
                review_priority,
                state.get("unsupported_language_reason"),
                state.get("evaluation_summary", ""),
                concerns_json,
                metrics_json
            ))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"[DB] Case {case_id} stored successfully")

            return {
                "success": True,
                "case_id": case_id,
                "review_priority": review_priority,
                "exit_reason": exit_reason
            }

        except psycopg2.Error as e:
            logger.error(f"[DB] PostgreSQL error storing case {case_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "case_id": case_id
            }
        except Exception as e:
            logger.error(f"[DB] Unexpected error storing case {case_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "case_id": case_id
            }

    def get_review_queue(
        self,
        limit: int = 50,
        priority_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get cases pending human review, ordered by priority.

        Priority order:
        1. URGENT (unsupported language or critical severity)
        2. HIGH (timeout with low confidence)
        3. NORMAL (confidence met, verification required)

        Args:
            limit: Maximum number of cases to return
            priority_filter: Optional filter for specific priority

        Returns:
            Dictionary with cases and counts
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Build query
            query = """
                SELECT * FROM cases
                WHERE requires_review = TRUE
                AND processing_mode = 'streaming'
            """
            params = []

            if priority_filter:
                query += " AND review_priority = %s"
                params.append(priority_filter)

            query += """
                ORDER BY
                    CASE review_priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        ELSE 3
                    END,
                    created_at ASC
                LIMIT %s
            """
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Get priority counts
            cursor.execute("""
                SELECT review_priority, COUNT(*) as count
                FROM cases
                WHERE requires_review = TRUE
                AND processing_mode = 'streaming'
                GROUP BY review_priority
            """)
            counts = {row["review_priority"]: row["count"] for row in cursor.fetchall()}

            cursor.close()
            conn.close()

            # Format cases with priority labels
            cases = []
            for row in rows:
                case = dict(row)
                priority = case.get("review_priority", "normal")
                exit_reason = case.get("exit_reason", "")

                # Format datetime
                if case.get("created_at"):
                    case["created_at"] = case["created_at"].isoformat()

                # Add priority icons and labels
                if exit_reason == "unsupported_language":
                    case["priority_icon"] = "LANG"
                    case["priority_label"] = "URGENT - Unsupported Language"
                elif priority == "urgent":
                    case["priority_icon"] = "CRIT"
                    case["priority_label"] = "URGENT - Critical Emergency"
                elif priority == "high":
                    case["priority_icon"] = "HIGH"
                    case["priority_label"] = "HIGH - AI Uncertain"
                else:
                    case["priority_icon"] = "NORM"
                    case["priority_label"] = "NORMAL - Verification Required"

                cases.append(case)

            return {
                "success": True,
                "total_count": sum(counts.values()),
                "urgent_count": counts.get("urgent", 0),
                "high_count": counts.get("high", 0),
                "normal_count": counts.get("normal", 0),
                "cases": cases
            }

        except psycopg2.Error as e:
            logger.error(f"[DB] Error getting review queue: {e}")
            return {
                "success": False,
                "error": str(e),
                "cases": []
            }
        except Exception as e:
            logger.error(f"[DB] Unexpected error getting review queue: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "cases": []
            }

    def get_case(self, case_id: str) -> Dict[str, Any]:
        """Get a specific streaming case by ID.

        Args:
            case_id: Case ID to retrieve

        Returns:
            Case data or error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM cases WHERE case_id = %s", (case_id,))
            case = cursor.fetchone()

            if not case:
                cursor.close()
                conn.close()
                return {
                    "success": False,
                    "error": f"Case not found: {case_id}"
                }

            # Get feedback if exists
            cursor.execute("SELECT * FROM feedback WHERE case_id = %s", (case_id,))
            feedback = cursor.fetchone()

            cursor.close()
            conn.close()

            case_dict = dict(case)
            if case_dict.get("created_at"):
                case_dict["created_at"] = case_dict["created_at"].isoformat()

            return {
                "success": True,
                "case": case_dict,
                "feedback": dict(feedback) if feedback else None,
                "has_been_reviewed": feedback is not None
            }

        except psycopg2.Error as e:
            logger.error(f"[DB] Error getting case {case_id}: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[DB] Unexpected error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def complete_review(
        self,
        case_id: str,
        reviewer_id: str,
        approved_incident: str,
        approved_severity: str,
        approved_unit: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete human review and save to feedback table.

        Args:
            case_id: Case ID being reviewed
            reviewer_id: ID of the human reviewer
            approved_incident: Final incident type (AI or corrected)
            approved_severity: Final severity level (AI or corrected)
            approved_unit: Final dispatch unit (AI or corrected)
            notes: Optional review notes

        Returns:
            Dictionary with success status and feedback_id
        """
        feedback_id = f"feedback-{uuid4().hex[:12]}"

        logger.info(f"[DB] Completing review for case {case_id} by {reviewer_id}")

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Insert or update feedback
            cursor.execute("""
                INSERT INTO feedback (
                    feedback_id, case_id, corrected_incident,
                    corrected_severity, corrected_unit, operator_id, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (case_id) DO UPDATE SET
                    corrected_incident = EXCLUDED.corrected_incident,
                    corrected_severity = EXCLUDED.corrected_severity,
                    corrected_unit = EXCLUDED.corrected_unit,
                    operator_id = EXCLUDED.operator_id,
                    timestamp = EXCLUDED.timestamp
            """, (
                feedback_id, case_id, approved_incident,
                approved_severity, approved_unit, reviewer_id, datetime.utcnow()
            ))

            # Mark case as reviewed
            cursor.execute("""
                UPDATE cases SET requires_review = FALSE WHERE case_id = %s
            """, (case_id,))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"[DB] Review completed for case {case_id}")

            return {
                "success": True,
                "case_id": case_id,
                "feedback_id": feedback_id,
                "reviewed_by": reviewer_id,
                "reviewed_at": datetime.utcnow().isoformat()
            }

        except psycopg2.Error as e:
            logger.error(f"[DB] Error completing review: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[DB] Unexpected error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


def create_streaming_case_controller(db_config: Dict[str, Any]) -> StreamingCaseController:
    """Factory function to create StreamingCaseController.

    Args:
        db_config: Database configuration dictionary

    Returns:
        Configured StreamingCaseController instance
    """
    return StreamingCaseController(db_config)
