"""
Database initialization script for PostgreSQL

This script:
1. Loads environment variables from .env file
2. Creates the emergency_dispatch database if it doesn't exist
3. Creates cases and feedback tables with proper indexes
"""

import os
import sys
import logging
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
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
    # Get the project root directory (parent of data/)
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
    # Get path relative to project root
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
    # Load .env file first
    load_env_file()

    # Try to load from config
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
        # Fallback to environment variables only
        params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'emergency_dispatch'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }

    return params


def test_connection(params):
    """Test if we can connect to PostgreSQL server."""
    test_params = params.copy()
    test_params.pop('database', None)  # Remove database for initial connection

    try:
        conn = psycopg2.connect(database='postgres', **test_params)
        conn.close()
        return True, None
    except psycopg2.OperationalError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def create_database():
    """Create the database if it doesn't exist."""
    params = get_db_connection_params()
    db_name = params.pop('database')

    # Test connection first
    print("\nTesting PostgreSQL connection...")
    logger.info(f"Connecting to PostgreSQL at {params['host']}:{params['port']}")

    success, error = test_connection(params)
    if not success:
        print(f"❌ Cannot connect to PostgreSQL server!")
        print(f"   Error: {error}")
        print(f"\nTroubleshooting:")
        print(f"   1. Ensure PostgreSQL is installed and running")
        print(f"   2. Check connection settings in .env file:")
        print(f"      DB_HOST={params['host']}")
        print(f"      DB_PORT={params['port']}")
        print(f"      DB_USER={params['user']}")
        print(f"   3. Verify PostgreSQL is accepting connections:")
        print(f"      - On Linux/Mac: sudo systemctl status postgresql")
        print(f"      - On Windows: Check Services for PostgreSQL")
        sys.exit(1)

    print("✓ PostgreSQL connection successful")

    try:
        # Connect to PostgreSQL server (default 'postgres' database)
        conn = psycopg2.connect(database='postgres', **params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists (using parameterized query)
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()

        if not exists:
            # Create database using sql.Identifier to prevent SQL injection
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
            )
            print(f"✓ Database '{db_name}' created successfully")
            logger.info(f"Database '{db_name}' created")
        else:
            print(f"✓ Database '{db_name}' already exists")
            logger.info(f"Database '{db_name}' already exists")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {e}")
        print(f"❌ Database creation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        return False


def init_cases_table():
    """Initialize the cases table."""
    params = get_db_connection_params()

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        # Create cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id VARCHAR(36) PRIMARY KEY,
                transcript TEXT NOT NULL,
                detected_language VARCHAR(10),
                language_confidence REAL,
                ai_incident VARCHAR(100),
                ai_severity VARCHAR(50),
                ai_unit VARCHAR(100),
                incident_confidence REAL,
                severity_confidence REAL,
                dispatch_confidence REAL,
                requires_review BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cases_created_at
            ON cases(created_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cases_requires_review
            ON cases(requires_review)
            WHERE requires_review = TRUE
        """)

        conn.commit()
        cursor.close()
        conn.close()

        print("✓ Cases table initialized successfully")
        logger.info("Cases table initialized")
        return True

    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error creating cases table: {e}")
        print(f"❌ Error creating cases table: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        return False


def init_feedback_table():
    """Initialize the feedback table."""
    params = get_db_connection_params()

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        # Create feedback table with foreign key
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id VARCHAR(36) PRIMARY KEY,
                case_id VARCHAR(36) NOT NULL,
                corrected_incident VARCHAR(100),
                corrected_severity VARCHAR(50),
                corrected_unit VARCHAR(100),
                operator_id VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            )
        """)

        # Create index on case_id for faster joins
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_case_id
            ON feedback(case_id)
        """)

        # Create index on timestamp
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_timestamp
            ON feedback(timestamp DESC)
        """)

        conn.commit()
        cursor.close()
        conn.close()

        print("✓ Feedback table initialized successfully")
        logger.info("Feedback table initialized")
        return True

    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error creating feedback table: {e}")
        print(f"❌ Error creating feedback table: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        return False


def verify_tables():
    """Verify that all tables were created successfully."""
    params = get_db_connection_params()

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('cases', 'feedback')
            ORDER BY table_name
        """)

        tables = [row[0] for row in cursor.fetchall()]

        print("\n" + "=" * 50)
        print("Database Verification")
        print("=" * 50)

        if 'cases' in tables:
            print("✓ Table 'cases' exists")
        else:
            print("✗ Table 'cases' missing")

        if 'feedback' in tables:
            print("✓ Table 'feedback' exists")
        else:
            print("✗ Table 'feedback' missing")

        # Check indexes
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('cases', 'feedback')
            ORDER BY indexname
        """)

        indexes = [row[0] for row in cursor.fetchall()]
        print(f"✓ {len(indexes)} indexes created")

        cursor.close()
        conn.close()

        return len(tables) == 2

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        print(f"❌ Verification failed: {e}")
        return False


def initialize_databases():
    """Initialize PostgreSQL database and all tables."""
    print("\n" + "=" * 50)
    print("PostgreSQL Database Initialization")
    print("=" * 50)

    all_success = True

    try:
        # Step 1: Create database
        print("\n[1/3] Creating database...")
        if not create_database():
            all_success = False
            print("\n❌ Database creation failed!")
            sys.exit(1)

        # Step 2: Create cases table
        print("\n[2/3] Creating tables...")
        if not init_cases_table():
            all_success = False

        # Step 3: Create feedback table
        if not init_feedback_table():
            all_success = False

        if not all_success:
            print("\n❌ Some tables failed to initialize!")
            sys.exit(1)

        # Step 4: Verify everything
        print("\n[3/3] Verifying database setup...")
        if not verify_tables():
            print("\n⚠️  Verification failed, but tables may still work")

        print("\n" + "=" * 50)
        print("✓ Database initialization completed successfully!")
        print("=" * 50)
        print("\nYou can now run: python main.py")
        logger.info("Database initialization completed successfully")

    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    initialize_databases()
