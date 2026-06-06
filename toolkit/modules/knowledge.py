"""Local Knowledge Base - Store and retrieve learned information."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "knowledge.db"


def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def save(category, title, content, source=None, tags=None):
    """Save a knowledge entry."""
    conn = _get_db()
    tags_str = json.dumps(tags) if tags else "[]"
    conn.execute(
        "INSERT INTO knowledge (category, title, content, source, tags) VALUES (?, ?, ?, ?, ?)",
        (category, title, content, source, tags_str)
    )
    conn.commit()
    conn.close()
    return True, None


def search(query, category=None, limit=10):
    """Search knowledge base."""
    conn = _get_db()
    if category:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE category=? AND (title LIKE ? OR content LIKE ?) LIMIT ?",
            (category, f"%{query}%", f"%{query}%", limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE title LIKE ? OR content LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        ).fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row[0], "category": row[1], "title": row[2],
            "content": row[3], "source": row[4], "tags": json.loads(row[5]),
            "created_at": row[6], "updated_at": row[7]
        })
    return results, None


def list_categories():
    """List all categories."""
    conn = _get_db()
    rows = conn.execute("SELECT DISTINCT category, COUNT(*) FROM knowledge GROUP BY category").fetchall()
    conn.close()
    return [{"category": r[0], "count": r[1]} for r in rows], None


def memory_set(key, value):
    """Store a key-value memory."""
    conn = _get_db()
    conn.execute(
        "INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, ?)",
        (key, value, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return True, None


def memory_get(key):
    """Retrieve a key-value memory."""
    conn = _get_db()
    row = conn.execute("SELECT value FROM memory WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else None, None


def memory_list():
    """List all memories."""
    conn = _get_db()
    rows = conn.execute("SELECT key, value, updated_at FROM memory ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [{"key": r[0], "value": r[1], "updated": r[2]} for r in rows], None
