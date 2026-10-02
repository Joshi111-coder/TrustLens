import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.config import settings

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            message_preview TEXT NOT NULL,
            full_text TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            summary TEXT NOT NULL,
            red_flags TEXT NOT NULL,
            claims TEXT NOT NULL,
            recommended_actions TEXT NOT NULL,
            action_dos TEXT NOT NULL,
            action_donts TEXT NOT NULL,
            why_flagged TEXT NOT NULL,
            trusted_sources TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            language_name TEXT DEFAULT 'English'
        )
    """)
    # Check if language columns exist for existing database file
    cursor.execute("PRAGMA table_info(analysis_history)")
    existing_cols = {col[1] for col in cursor.fetchall()}
    if "language" not in existing_cols:
        cursor.execute("ALTER TABLE analysis_history ADD COLUMN language TEXT DEFAULT 'en'")
    if "language_name" not in existing_cols:
        cursor.execute("ALTER TABLE analysis_history ADD COLUMN language_name TEXT DEFAULT 'English'")
        
    conn.commit()
    conn.close()

def save_analysis(data: Dict[str, Any]) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    
    analysis_id = data.get("id")
    created_at = data.get("created_at") or datetime.utcnow().isoformat()
    raw_text = data.get("raw_text", "")
    preview = (raw_text[:120] + "...") if len(raw_text) > 120 else raw_text
    
    cursor.execute("""
        INSERT OR REPLACE INTO analysis_history (
            id, created_at, message_preview, full_text,
            risk_level, risk_score, summary,
            red_flags, claims, recommended_actions,
            action_dos, action_donts, why_flagged, trusted_sources,
            language, language_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        analysis_id,
        created_at,
        preview,
        raw_text,
        data.get("risk_level", "NEEDS VERIFICATION"),
        data.get("risk_score", 50),
        data.get("summary", ""),
        json.dumps(data.get("red_flags", [])),
        json.dumps(data.get("claims", [])),
        json.dumps(data.get("recommended_actions", [])),
        json.dumps(data.get("action_dos", [])),
        json.dumps(data.get("action_donts", [])),
        json.dumps(data.get("why_flagged", [])),
        json.dumps(data.get("trusted_sources", [])),
        data.get("language", "en"),
        data.get("language_name", "English")
    ))
    
    conn.commit()
    conn.close()
    return analysis_id

def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, message_preview, risk_level, risk_score, red_flags
        FROM analysis_history
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    
    history = []
    for row in rows:
        red_flags_parsed = []
        try:
            red_flags_parsed = json.loads(row["red_flags"])
        except Exception:
            pass
            
        history.append({
            "id": row["id"],
            "created_at": row["created_at"],
            "message_preview": row["message_preview"],
            "risk_level": row["risk_level"],
            "risk_score": row["risk_score"],
            "red_flags_count": len(red_flags_parsed)
        })
    conn.close()
    return history

def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM analysis_history WHERE id = ?
    """, (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "raw_text": row["full_text"],
        "risk_level": row["risk_level"],
        "risk_score": row["risk_score"],
        "summary": row["summary"],
        "red_flags": json.loads(row["red_flags"]),
        "claims": json.loads(row["claims"]),
        "recommended_actions": json.loads(row["recommended_actions"]),
        "action_dos": json.loads(row["action_dos"]),
        "action_donts": json.loads(row["action_donts"]),
        "why_flagged": json.loads(row["why_flagged"]),
        "trusted_sources": json.loads(row["trusted_sources"]),
        "language": row["language"] if "language" in row.keys() else "en",
        "language_name": row["language_name"] if "language_name" in row.keys() else "English"
    }
