"""
Test PostgreSQL Database Connection

This script tests the database connection and verifies all tables are set up correctly.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_params():
    """Get database connection parameters."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'emergency_dispatch'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }


def test_connection():
    """Test database connection."""
    print("Testing PostgreSQL connection...")
    print("=" * 60)

    params = get_db_params()
    print(f"Host: {params['host']}")
    print(f"Port: {params['port']}")
    print(f"Database: {params['database']}")
    print(f"User: {params['user']}")
    print("=" * 60)

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print("\n✓ Connection successful!")
        print(f"PostgreSQL version: {version}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        return False


def test_tables():
    """Test if all required tables exist."""
    print("\n" + "=" * 60)
    print("Checking database tables...")
    print("=" * 60)

    params = get_db_params()

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check for cases table
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'cases'
            ORDER BY ordinal_position;
        """)
        cases_columns = cursor.fetchall()

        if cases_columns:
            print("\n✓ 'cases' table exists")
            print("  Columns:")
            for col in cases_columns:
                print(f"    - {col['column_name']} ({col['data_type']})")
        else:
            print("\n✗ 'cases' table not found")

        # Check for feedback table
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'feedback'
            ORDER BY ordinal_position;
        """)
        feedback_columns = cursor.fetchall()

        if feedback_columns:
            print("\n✓ 'feedback' table exists")
            print("  Columns:")
            for col in feedback_columns:
                print(f"    - {col['column_name']} ({col['data_type']})")
        else:
            print("\n✗ 'feedback' table not found")

        # Check indexes
        cursor.execute("""
            SELECT indexname, tablename
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('cases', 'feedback');
        """)
        indexes = cursor.fetchall()

        if indexes:
            print("\n✓ Indexes found:")
            for idx in indexes:
                print(f"    - {idx['indexname']} on {idx['tablename']}")

        # Get row counts
        cursor.execute("SELECT COUNT(*) as count FROM cases;")
        cases_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM feedback;")
        feedback_count = cursor.fetchone()['count']

        print(f"\nRow counts:")
        print(f"  - cases: {cases_count}")
        print(f"  - feedback: {feedback_count}")

        cursor.close()
        conn.close()

        return len(cases_columns) > 0 and len(feedback_columns) > 0

    except Exception as e:
        print(f"\n✗ Table check failed: {e}")
        return False


def test_write_read():
    """Test write and read operations."""
    print("\n" + "=" * 60)
    print("Testing write and read operations...")
    print("=" * 60)

    params = get_db_params()

    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Test insert
        test_case_id = 'test-connection-case-123'

        # Clean up any existing test data
        cursor.execute("DELETE FROM cases WHERE case_id = %s", (test_case_id,))

        cursor.execute("""
            INSERT INTO cases (
                case_id, transcript, detected_language, language_confidence,
                ai_incident, ai_severity, ai_unit,
                incident_confidence, severity_confidence, dispatch_confidence,
                requires_review
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_case_id, "Test transcript", "en", 0.95,
            "TEST", "LOW", "TEST_UNIT", 0.9, 0.85, 0.88, False
        ))

        conn.commit()
        print("✓ Test record inserted")

        # Test read
        cursor.execute("SELECT * FROM cases WHERE case_id = %s", (test_case_id,))
        result = cursor.fetchone()

        if result and result['transcript'] == "Test transcript":
            print("✓ Test record retrieved successfully")

            # Clean up
            cursor.execute("DELETE FROM cases WHERE case_id = %s", (test_case_id,))
            conn.commit()
            print("✓ Test record cleaned up")

            cursor.close()
            conn.close()
            return True
        else:
            print("✗ Test record not found or data mismatch")
            cursor.close()
            conn.close()
            return False

    except Exception as e:
        print(f"✗ Write/Read test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PostgreSQL Database Connection Test")
    print("=" * 60)

    results = {
        'connection': False,
        'tables': False,
        'operations': False
    }

    # Test connection
    results['connection'] = test_connection()

    if results['connection']:
        # Test tables
        results['tables'] = test_tables()

        if results['tables']:
            # Test operations
            results['operations'] = test_write_read()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Connection: {'✓ PASS' if results['connection'] else '✗ FAIL'}")
    print(f"Tables: {'✓ PASS' if results['tables'] else '✗ FAIL'}")
    print(f"Operations: {'✓ PASS' if results['operations'] else '✗ FAIL'}")
    print("=" * 60)

    if all(results.values()):
        print("\n🎉 All tests passed! PostgreSQL is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is installed and running")
        print("2. Check your .env file has correct database credentials")
        print("3. Run 'python data/init_db.py' to initialize the database")
        return 1


if __name__ == "__main__":
    sys.exit(main())
