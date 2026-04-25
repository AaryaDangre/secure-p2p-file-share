import sqlite3
from datetime import datetime
from .database import get_connection, close_connection


def init_db():
    """Initialize transfers table if not exists"""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filesize INTEGER NOT NULL,
                peer_ip TEXT NOT NULL,
                port INTEGER NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        close_connection(conn)


def log_transfer(filename: str, filesize: int, peer_ip: str, port: int, status: str):
    """Log file transfer to database"""
    conn = get_connection()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("""
            INSERT INTO transfers (filename, filesize, peer_ip, port, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (filename, filesize, peer_ip, port, status, timestamp))
        conn.commit()
    finally:
        close_connection(conn)


def get_all_transfers():
    """Get all transfer records"""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT * FROM transfers ORDER BY timestamp DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        close_connection(conn)


def get_transfers_by_status(status: str):
    """Get transfers by status"""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT * FROM transfers WHERE status = ? ORDER BY timestamp DESC
        """, (status,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        close_connection(conn)
