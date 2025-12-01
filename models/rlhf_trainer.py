# RLHF Trainer
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class RLHFTrainer:
    def __init__(self, db_config: Dict[str, Any], min_samples: int = 10):
        self.db_config = db_config
        self.min_samples = min_samples

    def _get_db_connection(self):
        """Get a PostgreSQL database connection."""
        return psycopg2.connect(
            host=self.db_config.get('host', 'localhost'),
            port=self.db_config.get('port', 5432),
            database=self.db_config.get('database', 'emergency_dispatch'),
            user=self.db_config.get('user', 'postgres'),
            password=self.db_config.get('password', 'postgres')
        )

    def collect_feedback(self) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT f.*, c.transcript, c.ai_incident, c.ai_severity, c.ai_unit,
                       c.detected_language
                FROM feedback f
                JOIN cases c ON f.case_id = c.case_id
                ORDER BY f.timestamp DESC
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to collect feedback: {e}")
            return []

    def train(self) -> Dict[str, Any]:
        feedback = self.collect_feedback()
        if len(feedback) >= self.min_samples:
            return {
                "status": "completed",
                "feedback_count": len(feedback),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "skipped",
                "reason": "insufficient_feedback",
                "feedback_count": len(feedback),
                "required": self.min_samples
            }

def create_rlhf_trainer(config: Dict) -> RLHFTrainer:
    db_config = config.get("database", {})
    rlhf_config = config.get("rlhf", {})
    return RLHFTrainer(
        db_config=db_config,
        min_samples=rlhf_config.get("min_feedback_samples", 10)
    )

