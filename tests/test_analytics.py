"""Run from the project folder:  python -m unittest tests.test_analytics -v"""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import database.db as dbm

dbm.DB_PATH = Path(tempfile.mkdtemp()) / "test_analytics.db"  # never touch the real database
dbm.init_db()

from database import analytics_repository as repo  # noqa: E402
from database import roadmap_repository as roadmap_repo  # noqa: E402
from database.db import get_connection  # noqa: E402
from services import analytics as A  # noqa: E402
from services.roadmap_generator import generate_roadmap  # noqa: E402

TODAY = date(2026, 11, 18)


def _raw_with_events(days_ago_hours):
    raw = A.load_raw(today=TODAY, record=False)
    raw["events"] = [{"skill": f"S{i}", "date": TODAY - timedelta(days=d), "hours": h, "stage": "Stage", "group": "Other"}
                     for i, (d, h) in enumerate(days_ago_hours)]
    return raw


class LearningTests(unittest.TestCase):
    def test_hours_windows_and_streak(self):
        raw = _raw_with_events([(0, 4), (1, 6), (3, 2), (20, 10), (45, 8)])
        L = A.build_dashboard(raw, "30 Days")["learning"]
        self.assertEqual(L["today_hours"], 4)
        self.assertEqual(L["week_hours"], 12)
        self.assertEqual(L["month_hours"], 22)
        self.assertEqual(L["window_hours"], 22)
        self.assertEqual(L["prev_hours"], 8)      # days 30-59 ago
        self.assertEqual(L["streak"], 2)
        self.assertEqual(L["active_days"], 4)
        self.assertEqual(L["consistency"], round(100 * 4 / 30))
        self.assertEqual(A.build_dashboard(raw, "All Time")["learning"]["window_hours"], 30)

    def test_no_activity_is_empty_not_zero_stat(self):
        d = A.build_dashboard(_raw_with_events([]), "30 Days")
        self.assertFalse(d["learning"]["has_data"])
        self.assertIsNone(d["learning"]["consistency"])
        hours = next(c for c in d["cards"] if c["key"] == "hours")
        self.assertIsNone(hours["value"])

    def test_weekly_has_seven_days_ending_today(self):
        w = A.build_dashboard(_raw_with_events([(0, 3)]), "7 Days")["learning"]["weekly"]
        self.assertEqual(len(w), 7)
        self.assertEqual(w[-1]["date"], TODAY)
        self.assertEqual(w[-1]["hours"], 3)


class EmptyStateTests(unittest.TestCase):
    def test_fresh_user_has_no_invented_values(self):
        d = A.build_dashboard(A.load_raw(today=TODAY, record=False), "30 Days")
        self.assertFalse(d["roadmap"]["has_roadmap"])
        self.assertFalse(d["cv"]["has_cv"])
        self.assertFalse(d["career"]["has_career"])
        cards = {c["key"]: c for c in d["cards"]}
        self.assertIsNone(cards["career"]["value"])
        self.assertIsNone(cards["skills"]["value"])
        self.assertIsNotNone(cards["match"]["value"])   # computed from profile skills and the job catalogue

    def test_unknown_window_rejected(self):
        with self.assertRaises(ValueError):
            A.build_dashboard(A.load_raw(today=TODAY, record=False), "1 Year")


class RoadmapTests(unittest.TestCase):
    def test_progress_and_acquired_skills_come_from_roadmap(self):
        plan = generate_roadmap("Backend Developer", "Intermediate", 2, ["Python", "Git"], today=TODAY)
        rid = roadmap_repo.replace_roadmap(plan, ["Python", "Git"], True)
        names = [s["name"] for st in plan["stages"] for s in st["skills"]]
        for n in names[:2]:
            roadmap_repo.set_completed(rid, n, True)
        with get_connection() as c:
            c.execute("UPDATE roadmap_progress SET completed_at=datetime('now','-1 day') WHERE roadmap_id=?", (rid,))
        raw = A.load_raw(record=False)
        d = A.build_dashboard(raw, "All Time")
        self.assertTrue(d["roadmap"]["has_roadmap"])
        self.assertEqual(d["roadmap"]["done"], 2)
        self.assertEqual(d["roadmap"]["total"], len(names))
        self.assertEqual(d["roadmap"]["done"] + len(d["roadmap"]["upcoming"]), len(names))
        self.assertEqual(d["skills"]["acquired_total"], 2)
        expected = sum(s["hours"] for st in plan["stages"] for s in st["skills"] if s["name"] in names[:2])
        self.assertEqual(d["learning"]["total_hours"], expected)


class SnapshotTests(unittest.TestCase):
    def test_one_snapshot_per_day_and_history(self):
        vals = dict(readiness=40, avg_match=50.0, best_match=70, strong_matches=2, top5_avg=60.0, jobs_analyzed=36, skills_count=5,
                    cv_score=None, roadmap_pct=None)
        repo.save_snapshot("2026-11-10", vals)
        repo.save_snapshot("2026-11-10", {**vals, "readiness": 45})
        rows = [r for r in repo.list_snapshots() if r["snap_date"] == "2026-11-10"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["readiness"], 45)
        raw = A.load_raw(today=TODAY, record=True)
        self.assertEqual(raw["snapshots"][-1]["snap_date"], TODAY.isoformat())
        jobs = A.build_dashboard(raw, "30 Days")["jobs"]
        self.assertGreaterEqual(len(jobs["history"]), 2)


if __name__ == "__main__":
    unittest.main()
