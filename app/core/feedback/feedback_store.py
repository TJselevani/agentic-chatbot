# app/feedback/feedback_store.py

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "feedback.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            session_id TEXT,
            intent TEXT,
            message TEXT,
            bot_response TEXT,
            rating INTEGER,
            comment TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_feedback(user_id: str, session_id: str, intent: str,
                  message: str, bot_response: str, rating: int, comment: str = None):
    """Store user feedback"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (user_id, session_id, intent, message, bot_response, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, session_id, intent, message, bot_response, rating, comment, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_feedback_summary():
    """Aggregate average ratings per intent"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT intent, AVG(rating) as avg_rating, COUNT(*) as total_feedback
        FROM feedback
        GROUP BY intent
    """)
    results = cursor.fetchall()
    conn.close()
    return [{"intent": r[0], "avg_rating": r[1], "count": r[2]} for r in results]


# Initialize DB
init_db()
