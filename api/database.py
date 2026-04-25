import sqlite3
import os

DB_FILE = "transfers.db"


def get_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn


def close_connection(conn):
    """Close database connection safely"""
    try:
        conn.close()
    except:
        pass
