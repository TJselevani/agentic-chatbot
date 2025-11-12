# app/memory/conversation_store.py

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "conversations.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            session_id TEXT,
            history TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_conversation(user_id: str, session_id: str, history: list):
    """Save or update conversation history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    history_json = json.dumps(history)
    cursor.execute("""
        INSERT OR REPLACE INTO conversations (user_id, session_id, history)
        VALUES (?, ?, ?)
    """, (user_id, session_id, history_json))
    conn.commit()
    conn.close()

def load_conversation(user_id: str, session_id: str):
    """Load a user's conversation history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT history FROM conversations
        WHERE user_id = ? AND session_id = ?
    """, (user_id, session_id))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return []

def clear_conversation(user_id: str, session_id: str):
    """Delete a user's conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE user_id = ? AND session_id = ?", (user_id, session_id))
    conn.commit()
    conn.close()

# Initialize database on module import
init_db()
