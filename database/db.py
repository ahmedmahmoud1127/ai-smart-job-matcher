"""SQLite connection, schema creation and sample-user seeding."""
import sqlite3
from pathlib import Path

from database.schema import ANALYTICS_SCHEMA, SKILL_GAP_SCHEMA, CV_SCHEMA, JOBS_SCHEMA, ROADMAP_SCHEMA

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "ai_job_matcher.db"
SAMPLE_USER_ID = 1  # the seeded demo account (also the fallback outside Streamlit, e.g. tests)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL, email TEXT NOT NULL,
    phone TEXT DEFAULT '', country TEXT DEFAULT '', city TEXT DEFAULT '',
    linkedin TEXT DEFAULT '', github TEXT DEFAULT '', portfolio TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    university TEXT NOT NULL, faculty TEXT NOT NULL, major TEXT NOT NULL, degree TEXT NOT NULL,
    academic_year TEXT DEFAULT '', graduation_year INTEGER, gpa REAL
);
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL, category TEXT NOT NULL, level TEXT NOT NULL,
    UNIQUE(user_id, name COLLATE NOCASE)
);
CREATE TABLE IF NOT EXISTS work_experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_title TEXT NOT NULL, company TEXT NOT NULL, employment_type TEXT NOT NULL,
    start_date TEXT NOT NULL, end_date TEXT DEFAULT '', description TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL, description TEXT NOT NULL, technologies TEXT NOT NULL,
    github_url TEXT NOT NULL, demo_url TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL, level TEXT NOT NULL,
    UNIQUE(user_id, name COLLATE NOCASE)
);
CREATE TABLE IF NOT EXISTS career_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    target_role TEXT DEFAULT '', target_role_other TEXT DEFAULT '',
    work_type TEXT DEFAULT '', employment_type TEXT DEFAULT '',
    industry TEXT DEFAULT '', industry_other TEXT DEFAULT ''
);
"""

SEED_SKILLS = [
    ("Python", "Programming Language", "Advanced"), ("SQL", "Database", "Intermediate"),
    ("HTML", "Web Development", "Advanced"), ("CSS", "Web Development", "Intermediate"),
    ("JavaScript", "Programming Language", "Intermediate"), ("Machine Learning", "Data & AI", "Intermediate"),
    ("Git & GitHub", "Tools & DevOps", "Intermediate"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables (if missing) and seed the sample user once."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.executescript(CV_SCHEMA)
        conn.executescript(JOBS_SCHEMA)
        conn.executescript(ROADMAP_SCHEMA)
        conn.executescript(SKILL_GAP_SCHEMA)
        conn.executescript(ANALYTICS_SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            uid = conn.execute(
                "INSERT INTO users (full_name,email,phone,country,city,linkedin,github) VALUES (?,?,?,?,?,?,?)",
                ("Ahmed Mahmoud", "ahmed.mahmoud@example.com", "+20 100 123 4567", "Egypt", "Cairo",
                 "https://linkedin.com/in/ahmed-mahmoud", "https://github.com/ahmed-mahmoud")).lastrowid
            conn.execute("INSERT INTO education (user_id,university,faculty,major,degree,academic_year,graduation_year,gpa)"
                         " VALUES (?,?,?,?,?,?,?,?)",
                         (uid, "Cairo University", "Faculty of Computers & AI", "Computer Science",
                          "Bachelor's", "4th Year", 2026, 3.5))
            conn.executemany("INSERT INTO skills (user_id,name,category,level) VALUES (?,?,?,?)",
                             [(uid, *s) for s in SEED_SKILLS])
            conn.executemany("INSERT INTO languages (user_id,name,level) VALUES (?,?,?)",
                             [(uid, "Arabic", "Native"), (uid, "English", "Advanced")])
            conn.execute("INSERT INTO career_preferences (user_id) VALUES (?)", (uid,))
