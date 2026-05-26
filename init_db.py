"""
Initialize SQLite database for experiment tracking.
Run once before starting data collection.
"""

import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'experiment.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Main experiment results table
    c.execute('''
    CREATE TABLE IF NOT EXISTS api_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id TEXT NOT NULL,
        persona_id TEXT NOT NULL,
        persona_type TEXT NOT NULL CHECK(persona_type IN ('demographic','biographical','interview')),
        model TEXT NOT NULL CHECK(model IN ('gpt-4o','claude-3.5-sonnet','llama-3.3-70b','deepseek-v4-flash')),
        run_number INTEGER NOT NULL CHECK(run_number IN (1, 2, 3)),
        ab_order TEXT NOT NULL CHECK(ab_order IN ('original','swapped','random')),
        raw_response TEXT,
        parsed_choice TEXT CHECK(parsed_choice IN ('A','B','INVALID')),
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        response_time_ms INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','completed','failed','retry')),
        error_message TEXT,
        UNIQUE(test_id, persona_id, model, run_number, ab_order)
    )
    ''')

    # Position bias measurement, no persona
    c.execute('''
    CREATE TABLE IF NOT EXISTS position_bias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id TEXT NOT NULL,
        model TEXT NOT NULL,
        run_number INTEGER NOT NULL,
        ab_order TEXT NOT NULL CHECK(ab_order IN ('original','swapped')),
        raw_response TEXT,
        choice TEXT CHECK(choice IN ('A','B','INVALID')),
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Pilot results for test case selection
    c.execute('''
    CREATE TABLE IF NOT EXISTS pilot_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id TEXT NOT NULL,
        persona_id TEXT NOT NULL,
        model TEXT NOT NULL,
        choice TEXT CHECK(choice IN ('A','B','INVALID')),
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Human validation responses
    c.execute('''
    CREATE TABLE IF NOT EXISTS human_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id TEXT NOT NULL,
        participant_age INTEGER,
        participant_gender TEXT,
        participant_country TEXT,
        test_id TEXT NOT NULL,
        choice TEXT CHECK(choice IN ('A','B')),
        confidence INTEGER CHECK(confidence BETWEEN 1 AND 5),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(participant_id, test_id)
    )
    ''')

    # Indexes for fast queries
    c.execute('CREATE INDEX IF NOT EXISTS idx_api_status ON api_calls(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_api_model ON api_calls(model)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_api_persona_type ON api_calls(persona_type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_api_test ON api_calls(test_id)')

    conn.commit()
    conn.close()

    print(f"Database initialized at {os.path.abspath(DB_PATH)}")
    print("Tables: api_calls, position_bias, pilot_results, human_responses")


if __name__ == '__main__':
    init_db()
