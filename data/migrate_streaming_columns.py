"""
Database Migration: Add Streaming Columns

Adds new columns to the cases table for streaming processing metrics.
Uses IF NOT EXISTS / ADD COLUMN IF NOT EXISTS for safety.
This migration can be run multiple times without error.

Run: python -m data.migrate_streaming_columns

Columns added:
- processing_mode: Identifies batch vs streaming processing
- total_processing_time_ms: Total end-to-end processing time
- stt_time_ms: Speech-to-text processing time
- classification_time_ms: Total classification pipeline time
- evaluation_time_ms: Confidence gate evaluation time
- chunks_processed: Number of audio chunks processed
- evaluation_window_seconds: Configured evaluation window
- exit_reason: Why streaming exited (confidence_met, timeout, critical_severity, unsupported_language)
- review_priority: Human review priority (urgent, high, normal)
- unsupported_language_reason: Explanation for unsupported language cases
- evaluation_summary: Summary of evaluation results
- concerns: JSON array of concerns identified
- processing_metrics: Full JSON metrics object
"""

import os
import sys
import logging
from pathlib import Path

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env_file():
    """Load environment variables from .env file."""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    env_file = project_root / '.env'

    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from {env_file}")
        return True
    else:
        logger.warning(f".env file not found at {env_file}")
        return False


def load_config():
    """Load database configuration from config file."""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    config_path = project_root / "config" / "config.yaml"

    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('database', {})
        except Exception as e:
            logger.warning(f"Could not load config file: {e}")
            return None
    return None


def get_db_connection_params():
    """Get database connection parameters from environment or config."""
    load_env_file()
    config = load_config()

    if config:
        params = {
            'host': os.getenv('DB_HOST', config.get('host', 'localhost')),
            'port': int(os.getenv('DB_PORT', str(config.get('port', 5432)))),
            'database': os.getenv('DB_NAME', config.get('database', 'emergency_dispatch')),
            'user': os.getenv('DB_USER', config.get('user', 'postgres')),
            'password': os.getenv('DB_PASSWORD', config.get('password', 'postgres'))
        }
    else:
        params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'emergency_dispatch'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }

    return params


def run_migration():
    """Run the streaming columns migration."""
    params = get_db_connection_params()

    print("\n" + "=" * 60)
    print("Streaming Columns Migration")
    print("=" * 60)
    print(f"\nConnecting to: {params['host']}:{params['port']}/{params['database']}")

    logger.info("Starting streaming columns migration...")

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        # List of migrations to run
        migrations = [
            # Processing mode column
            ("processing_mode",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS processing_mode VARCHAR(20) DEFAULT 'batch'"),

            # Processing time metrics
            ("total_processing_time_ms",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS total_processing_time_ms REAL"),

            ("stt_time_ms",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS stt_time_ms REAL"),

            ("classification_time_ms",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS classification_time_ms REAL"),

            ("evaluation_time_ms",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS evaluation_time_ms REAL"),

            # Streaming-specific columns
            ("chunks_processed",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS chunks_processed INTEGER"),

            ("evaluation_window_seconds",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS evaluation_window_seconds REAL"),

            ("exit_reason",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS exit_reason VARCHAR(50)"),

            ("review_priority",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS review_priority VARCHAR(20) DEFAULT 'normal'"),

            ("unsupported_language_reason",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS unsupported_language_reason TEXT"),

            # Evaluation columns
            ("evaluation_summary",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS evaluation_summary TEXT"),

            ("concerns",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS concerns JSONB"),

            ("processing_metrics",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS processing_metrics JSONB"),

            # Updated timestamp
            ("updated_at",
             "ALTER TABLE cases ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP"),

            # Indexes for efficient querying
            ("idx_cases_processing_mode",
             "CREATE INDEX IF NOT EXISTS idx_cases_processing_mode ON cases(processing_mode)"),

            ("idx_cases_review_priority",
             "CREATE INDEX IF NOT EXISTS idx_cases_review_priority ON cases(review_priority) WHERE requires_review = TRUE"),

            ("idx_cases_exit_reason",
             "CREATE INDEX IF NOT EXISTS idx_cases_exit_reason ON cases(exit_reason)"),

            ("idx_cases_streaming_review",
             "CREATE INDEX IF NOT EXISTS idx_cases_streaming_review ON cases(processing_mode, review_priority, created_at DESC) WHERE requires_review = TRUE"),
        ]

        success_count = 0
        for name, sql_statement in migrations:
            try:
                print(f"  Running: {name}...")
                cursor.execute(sql_statement)
                logger.info(f"Migration '{name}' completed")
                success_count += 1
            except psycopg2.Error as e:
                logger.warning(f"Migration '{name}' warning: {e}")
                # Continue with other migrations

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n{success_count}/{len(migrations)} migrations completed successfully!")
        print("=" * 60)
        logger.info("Streaming columns migration completed!")

        return True

    except psycopg2.OperationalError as e:
        print(f"\nConnection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure PostgreSQL is running")
        print("  2. Check connection settings in .env or config.yaml")
        print("  3. Verify database exists (run: python -m data.init_db)")
        logger.error(f"Connection failed: {e}")
        return False

    except Exception as e:
        print(f"\nMigration failed: {e}")
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False


def verify_migration():
    """Verify that streaming columns were added."""
    params = get_db_connection_params()

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        # Check for new columns
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'cases'
            AND column_name IN (
                'processing_mode', 'total_processing_time_ms', 'stt_time_ms',
                'classification_time_ms', 'evaluation_time_ms', 'chunks_processed',
                'evaluation_window_seconds', 'exit_reason', 'review_priority',
                'unsupported_language_reason', 'evaluation_summary', 'concerns',
                'processing_metrics'
            )
            ORDER BY column_name
        """)

        columns = [row[0] for row in cursor.fetchall()]

        print("\nVerification - Streaming Columns Present:")
        expected_columns = [
            'chunks_processed', 'classification_time_ms', 'concerns',
            'evaluation_summary', 'evaluation_time_ms', 'evaluation_window_seconds',
            'exit_reason', 'processing_metrics', 'processing_mode',
            'review_priority', 'stt_time_ms', 'total_processing_time_ms',
            'unsupported_language_reason'
        ]

        for col in expected_columns:
            status = "OK" if col in columns else "MISSING"
            print(f"  {col}: {status}")

        # Check indexes
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'cases'
            AND indexname LIKE 'idx_cases_%'
            ORDER BY indexname
        """)

        indexes = [row[0] for row in cursor.fetchall()]
        print(f"\nIndexes found: {len(indexes)}")
        for idx in indexes:
            print(f"  - {idx}")

        cursor.close()
        conn.close()

        return len(columns) >= 10

    except Exception as e:
        print(f"\nVerification failed: {e}")
        logger.error(f"Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PostgreSQL Migration: Add Streaming Columns")
    print("=" * 60)

    success = run_migration()

    if success:
        verify_migration()
        print("\nMigration complete! You can now use the streaming workflow.")
    else:
        print("\nMigration failed. Please check the errors above.")
        sys.exit(1)
