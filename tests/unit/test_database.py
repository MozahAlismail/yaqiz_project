"""Unit tests for Database operations"""

import pytest
import sqlite3
import tempfile
import os
from data.init_db import init_cases_db, init_feedback_db


def test_init_cases_db():
    """Test cases database initialization."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_cases_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cases'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "cases"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_init_feedback_db():
    """Test feedback database initialization."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_feedback_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "feedback"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
