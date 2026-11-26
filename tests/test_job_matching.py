"""Run from the project folder:  python -m unittest tests.test_job_matching -v"""
import tempfile
import unittest
from pathlib import Path

import database.db as dbm
from data.jobs_catalog import JOBS
from data.skills_catalog import SKILL_CATEGORY

dbm.DB_PATH = Path(tempfile.mkdtemp()) / "test.db"  # never touch the real database
dbm.init_db()

from database import job_repository as job_repo  # noqa: E402
from database import repository as repo  # noqa: E402
from services import job_matching as jm  # noqa: E402


class JobMatchingTests(unittest.TestCase):
    def test_catalog_uses_known_skills(self):
        for j in JOBS:
            for s in j["required"] + j["preferred"]:
                self.assertIn(s, SKILL_CATEGORY, f"{j['title']}: unknown skill {s}")

    def test_scores_are_real_and_sorted(self):
        res = jm.rank_jobs(jm.build_candidate())
        scores = [r["score"] for r in res]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertGreater(len(set(scores)), 5)  # differentiated, not constant
        for r in res:
            self.assertTrue(0 <= r["score"] <= 100)
            self.assertAlmostEqual(sum(c["points"] for c in r["components"]), r["raw"], delta=0.3)

    def test_skills_drive_the_score(self):
        job = next(j for j in JOBS if j["title"] == "Junior Backend Developer")
        before = jm.score_job(job, jm.build_candidate())
        for name in ("Django", "REST APIs", "Docker", "Linux", "PostgreSQL", "Unit Testing"):
            try:
                repo.insert_row("skills", {"name": name, "category": "Other", "level": "Advanced"})
            except repo.DuplicateError:
                pass
        after = jm.score_job(job, jm.build_candidate())
        self.assertGreater(after["score"], before["score"])
        self.assertIn("Django", before["missing_required"])
        self.assertIn("Django", after["matched_required"])

    def test_related_skill_gives_partial_credit(self):
        cand = {"skills": {"MySQL": {"credit": 1.0, "sources": ["My Profile"]}}}
        credit, kind, via = jm._credit("SQL", cand["skills"])
        self.assertEqual((kind, via), ("related", "MySQL"))
        self.assertAlmostEqual(credit, 0.5)

    def test_what_if_recommendations(self):
        cand = jm.build_candidate()
        res = jm.rank_jobs(cand)
        rec = jm.recommend_skills(cand, res)
        self.assertTrue(rec["skills"])
        for s in rec["skills"]:
            self.assertGreater(s["avg_gain"], 0)
            self.assertNotIn(s["skill"], [k for k, v in cand["skills"].items() if v["credit"] >= jm.LEARN_CREDIT])

    def test_filters(self):
        res = jm.rank_jobs(jm.build_candidate())
        remote = jm.filter_jobs(res, work_type="Remote")
        self.assertTrue(remote and all(r["job"]["work_type"] == "Remote" for r in remote))
        self.assertTrue(all(r["score"] >= 60 for r in jm.filter_jobs(res, min_score=60)))
        self.assertTrue(all("python" in " ".join(r["job"]["required"] + r["job"]["preferred"] + [r["job"]["title"]]).lower()
                            for r in jm.filter_jobs(res, search="python")))
        self.assertEqual(jm.filter_jobs(res, search="no-such-thing-xyz"), [])

    def test_saved_jobs_persist(self):
        self.assertTrue(job_repo.toggle_saved("JM001"))
        self.assertIn("JM001", job_repo.saved_ids())
        self.assertFalse(job_repo.toggle_saved("JM001"))
        self.assertNotIn("JM001", job_repo.saved_ids())


if __name__ == "__main__":
    unittest.main()
