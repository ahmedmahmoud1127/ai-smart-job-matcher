"""Schema for the CV Analyzer feature (added on top of the Profile schema)."""

CV_SCHEMA = """
CREATE TABLE IF NOT EXISTS cv_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL, file_type TEXT DEFAULT '', file_size INTEGER DEFAULT 0, source_link TEXT DEFAULT '',
    extracted_text TEXT NOT NULL, target_role TEXT NOT NULL, score INTEGER NOT NULL,
    skills_json TEXT NOT NULL, result_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cv_user ON cv_analyses(user_id, id DESC);
"""

JOBS_SCHEMA = """
CREATE TABLE IF NOT EXISTS saved_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user ON saved_jobs(user_id, saved_at DESC);
"""

ROADMAP_SCHEMA = """
CREATE TABLE IF NOT EXISTS learning_roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career TEXT NOT NULL,
    level TEXT NOT NULL,
    hours_per_day REAL NOT NULL,
    include_bonus INTEGER NOT NULL DEFAULT 1,
    selected_skills TEXT NOT NULL DEFAULT '[]',
    plan_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS roadmap_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL REFERENCES learning_roadmaps(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(roadmap_id, skill)
);
CREATE INDEX IF NOT EXISTS idx_roadmaps_user ON learning_roadmaps(user_id, id DESC);
"""

SKILL_GAP_SCHEMA = """
CREATE TABLE IF NOT EXISTS skill_gap_state (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    career TEXT NOT NULL, level TEXT NOT NULL, hours_per_day REAL NOT NULL, focus TEXT NOT NULL DEFAULT 'Balanced',
    added_json TEXT NOT NULL DEFAULT '{}', removed_json TEXT NOT NULL DEFAULT '[]',
    result_json TEXT, generated_at TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

ANALYTICS_SCHEMA = """
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snap_date TEXT NOT NULL,
    readiness INTEGER, avg_match REAL, best_match INTEGER, strong_matches INTEGER, top5_avg REAL,
    jobs_analyzed INTEGER, skills_count INTEGER, cv_score INTEGER, roadmap_pct INTEGER,
    UNIQUE(user_id, snap_date)
);
CREATE INDEX IF NOT EXISTS idx_snapshots_user ON analytics_snapshots(user_id, snap_date);
"""
