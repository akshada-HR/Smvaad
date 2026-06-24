"""
init_db.py — Samvaad Database Initialiser
Runs on Streamlit Cloud startup to create and seed the SQLite database.
Called from app.py at the top of the file.
"""
import sqlite3, os, json, pathlib

DB_PATH  = pathlib.Path(__file__).parent / "employee.db"
SEED_PATH= pathlib.Path(__file__).parent / "seed_data.json"

def init():
    """Create all tables and seed data if the DB does not exist or is empty."""
    db_exists = DB_PATH.exists()
    conn = sqlite3.connect(str(DB_PATH))
    c    = conn.cursor()

    # ── CREATE TABLES ──────────────────────────────────────────────────────────
    c.executescript("""
    CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, department TEXT, designation TEXT,
        email TEXT, role TEXT DEFAULT 'Employee',
        password TEXT DEFAULT 'password',
        is_active INTEGER DEFAULT 1,
        joined_date TEXT,
        hr_level TEXT DEFAULT '',
        dept_access TEXT DEFAULT 'ALL'
    );

    CREATE TABLE IF NOT EXISTS survey_response (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER, motivation INTEGER, satisfaction INTEGER,
        team_connection INTEGER, recognition INTEGER, stress INTEGER,
        feedback TEXT, survey_date TEXT, enps INTEGER DEFAULT 7,
        sentiment_score REAL DEFAULT 0,
        eq_pressure REAL DEFAULT 3, eq_balance REAL DEFAULT 3,
        eq_empathy REAL DEFAULT 3, mindset_growth TEXT DEFAULT '',
        mindset_purpose TEXT DEFAULT '', mindset_clarity REAL DEFAULT 3,
        icebreaker_word TEXT DEFAULT '', icebreaker_emoji TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS survey_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_text TEXT NOT NULL, question_type TEXT NOT NULL,
        category TEXT NOT NULL, emoji TEXT DEFAULT '',
        options TEXT DEFAULT '', is_active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0, created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS survey_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_type TEXT, day_of_week TEXT,
        is_active INTEGER DEFAULT 1, created_by INTEGER, created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER, message TEXT,
        created_at TEXT, is_read INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS engagement_interventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, issue_category TEXT NOT NULL,
        department TEXT NOT NULL, description TEXT,
        recommended_action TEXT, priority TEXT DEFAULT 'Medium',
        owner TEXT, hrbp TEXT, manager_responsible TEXT,
        status TEXT DEFAULT 'Planned', created_date TEXT,
        start_date TEXT, due_date TEXT, completion_date TEXT,
        before_score REAL, before_burnout REAL,
        after_score REAL, after_burnout REAL,
        effectiveness_score REAL, linked_employee_id INTEGER,
        comments TEXT, created_by INTEGER
    );

    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT, value TEXT
    );
    """)
    conn.commit()

    # ── SEED DATA (only if employee table is empty) ────────────────────────────
    c.execute("SELECT COUNT(*) FROM employee")
    if c.fetchone()[0] == 0 and SEED_PATH.exists():
        with open(str(SEED_PATH)) as f:
            seed = json.load(f)

        for table, rows in seed.items():
            if not rows:
                continue
            cols   = list(rows[0].keys())
            # skip auto-increment id — let SQLite assign
            cols_no_id = [col for col in cols if col != 'id']
            placeholders = ','.join(['?' for _ in cols_no_id])
            sql = f"INSERT INTO {table} ({','.join(cols_no_id)}) VALUES ({placeholders})"
            for row in rows:
                values = [row[col] for col in cols_no_id]
                try:
                    c.execute(sql, values)
                except Exception:
                    pass  # skip duplicates silently
        conn.commit()
        print(f"[Samvaad] Database seeded from {SEED_PATH.name}")
    else:
        if db_exists:
            print("[Samvaad] Database already exists — skipping seed")
        else:
            print("[Samvaad] Seed file not found — starting with empty DB")

    conn.close()

if __name__ == "__main__":
    init()
    print("[Samvaad] init_db.py complete")
