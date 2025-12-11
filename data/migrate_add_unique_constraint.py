"""
Migration Script: Add UNIQUE constraint to feedback.case_id

This script adds a UNIQUE constraint to ensure one-to-one relationship
between cases and feedback.
"""

import os
import sys
import psycopg2
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


def migrate():
    """Add UNIQUE constraint to feedback.case_id."""
    print("\n" + "=" * 60)
    print("Database Migration: Add UNIQUE Constraint")
    print("=" * 60)

    try:
        params = get_db_params()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()

        # Check if constraint already exists
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'feedback'
            AND constraint_type = 'UNIQUE'
            AND constraint_name = 'feedback_case_id_key'
        """)

        if cursor.fetchone():
            print("✓ UNIQUE constraint already exists on feedback.case_id")
            cursor.close()
            conn.close()
            return

        print("\nAdding UNIQUE constraint to feedback.case_id...")

        # Check for duplicate case_ids before adding constraint
        cursor.execute("""
            SELECT case_id, COUNT(*)
            FROM feedback
            GROUP BY case_id
            HAVING COUNT(*) > 1
        """)

        duplicates = cursor.fetchall()

        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} cases with multiple feedbacks:")
            for case_id, count in duplicates:
                print(f"   - case_id: {case_id} has {count} feedbacks")

            print("\n⚠️  Removing duplicate feedbacks (keeping most recent)...")

            # For each case with duplicates, keep only the most recent feedback
            for case_id, _ in duplicates:
                cursor.execute("""
                    DELETE FROM feedback
                    WHERE case_id = %s
                    AND feedback_id NOT IN (
                        SELECT feedback_id
                        FROM feedback
                        WHERE case_id = %s
                        ORDER BY timestamp DESC
                        LIMIT 1
                    )
                """, (case_id, case_id))

            print(f"✓ Removed duplicate feedbacks")

        # Add UNIQUE constraint
        cursor.execute("""
            ALTER TABLE feedback
            ADD CONSTRAINT feedback_case_id_key UNIQUE (case_id)
        """)

        conn.commit()
        print("✓ UNIQUE constraint added successfully")

        # Verify constraint
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'feedback'
            AND constraint_type = 'UNIQUE'
        """)

        constraints = cursor.fetchall()
        print(f"\nUnique constraints on feedback table:")
        for constraint in constraints:
            print(f"  - {constraint[0]}")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print("\nEach case can now have only ONE feedback.")

    except psycopg2.Error as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    migrate()
