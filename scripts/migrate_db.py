import os
import sqlite3
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "experiment.db")
BACKUP_PATH = os.path.join(BASE_DIR, "data", "experiment_backup.db")

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    # Create a physical backup first
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"Created physical backup at {BACKUP_PATH}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("BEGIN TRANSACTION")

        # 1. Rename existing table
        c.execute("ALTER TABLE api_calls RENAME TO api_calls_old")

        # 2. Create new table with updated constraints (run_number BETWEEN 1 AND 9, and deepseek-v4-flash)
        c.execute('''
        CREATE TABLE api_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id TEXT NOT NULL,
            persona_id TEXT NOT NULL,
            persona_type TEXT NOT NULL CHECK(persona_type IN ('demographic','biographical','interview')),
            model TEXT NOT NULL CHECK(model IN ('gpt-4o','claude-3.5-sonnet','llama-3.3-70b','deepseek-v4-flash')),
            run_number INTEGER NOT NULL CHECK(run_number BETWEEN 1 AND 9),
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

        # 3. Copy data over
        # The schema matches exactly in column order, so SELECT * works.
        # But wait, earlier data might have 'deepseek-chat' instead of 'deepseek-v4-flash'.
        # Let's clean it up on the fly if needed.
        
        c.execute('''
        INSERT INTO api_calls (id, test_id, persona_id, persona_type, model, run_number, ab_order, raw_response, parsed_choice, prompt_tokens, completion_tokens, response_time_ms, timestamp, status, error_message)
        SELECT id, test_id, persona_id, persona_type, 
               CASE WHEN model = 'deepseek-chat' THEN 'deepseek-v4-flash' ELSE model END, 
               run_number, ab_order, raw_response, parsed_choice, prompt_tokens, completion_tokens, response_time_ms, timestamp, status, error_message
        FROM api_calls_old
        ''')

        # 4. Recreate Indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_api_status ON api_calls(status)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_api_model ON api_calls(model)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_api_persona_type ON api_calls(persona_type)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_api_test ON api_calls(test_id)')

        # 5. Drop old table
        c.execute("DROP TABLE api_calls_old")

        # 6. Also fix model name in position_bias table
        c.execute('''
        UPDATE position_bias 
        SET model = 'deepseek-v4-flash' 
        WHERE model = 'deepseek-chat'
        ''')
        updated_pb = c.execute("SELECT changes()").fetchone()[0]
        print(f"Updated {updated_pb} rows in position_bias (deepseek-chat → deepseek-v4-flash)")

        conn.commit()
        print("Successfully migrated api_calls schema! Data preserved.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed! Rolled back. Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
