import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "runs.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT,
            pr_number INTEGER,
            prompt_file TEXT,
            overall_score INTEGER,
            recommendation TEXT,
            scores TEXT,
            node_trace TEXT,
            final_report TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_run(state: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO runs
        (repo, pr_number, prompt_file, overall_score, recommendation,
         scores, node_trace, final_report, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        state.get("repo"),
        state.get("pr_number"),
        state.get("prompt_file_path"),
        state.get("scores", {}).get("overall"),
        state.get("recommendation"),
        json.dumps(state.get("scores", {})),
        json.dumps(state.get("node_trace", [])),
        state.get("final_report"),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def get_history(repo: str, prompt_file: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT overall_score, recommendation, created_at, pr_number
        FROM runs
        WHERE repo = ? AND prompt_file = ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (repo, prompt_file)).fetchall()
    conn.close()
    return [
        {
            "overall_score": r[0],
            "recommendation": r[1],
            "created_at": r[2],
            "pr_number": r[3]
        }
        for r in rows
    ]


def get_all_runs(repo: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT repo, pr_number, prompt_file, overall_score, 
               recommendation, created_at
        FROM runs
        WHERE repo = ?
        ORDER BY created_at DESC
        LIMIT 50
    """, (repo,)).fetchall()
    conn.close()
    return [
        {
            "repo": r[0],
            "pr_number": r[1],
            "prompt_file": r[2],
            "overall_score": r[3],
            "recommendation": r[4],
            "created_at": r[5]
        }
        for r in rows
    ]