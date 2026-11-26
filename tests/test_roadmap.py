"""Run from the project folder:  python -m unittest tests.test_roadmap -v"""
import tempfile
import unittest
from datetime import date
from pathlib import Path

import database.db as dbm
from data.roadmaps import CAREER_ROADMAPS, LEVELS, RESOURCES, SKILL_HOURS
from data.skills_catalog import SKILL_CATEGORY

dbm.DB_PATH = Path(tempfile.mkdtemp()) / "test_roadmap.db"  # never touch the real database
dbm.init_db()

from database import roadmap_repository as repo  # noqa: E402
from services import roadmap_generator as rg  # noqa: E402

BACKEND_ALL = [s for st in CAREER_ROADMAPS["Backend Developer"]["stages"] for s in st["core"] + st["bonus"]]


class RoadmapDataTests(unittest.TestCase):
    def test_every_skill_is_known_and_documented(self):
        for career, data in CAREER_ROADMAPS.items():
            self.assertTrue(data["stages"], career)
            seen = []
            for st in data["stages"]:
                self.assertTrue(st["core"], f"{career}/{st['name']} has no core skills")
                for s in st["core"] + st["bonus"]:
                    seen.append(s)
                    self.assertIn(s, SKILL_CATEGORY, s)
                    self.assertIn(s, RESOURCES, f"no resources for {s}")
                    self.assertIn(s, SKILL_HOURS, f"no hours for {s}")
            self.assertEqual(len(seen), len(set(seen)), f"duplicate skill in {career}")


class RoadmapLogicTests(unittest.TestCase):
    def test_missing_skills_are_found_automatically(self):
        plan = rg.generate_roadmap("Backend Developer", "Beginner", 2, ["Python", "Git"])
        missing = {s["name"] for st in plan["stages"] for s in st["skills"]}
        self.assertNotIn("Python", missing)
        self.assertNotIn("Git", missing)
        self.assertTrue({"SQL", "Django", "Docker"} <= missing)
        self.assertEqual(plan["missing_count"], len(missing))

    def test_knowing_everything_leaves_nothing_to_learn(self):
        plan = rg.generate_roadmap("Backend Developer", "Beginner", 2, BACKEND_ALL)
        self.assertEqual((plan["missing_count"], plan["total_hours"], plan["total_weeks"]), (0, 0, 0))
        self.assertEqual(rg.progress_summary(plan, set())["pct"], 100)

    def test_level_and_hours_change_the_estimate(self):
        beginner = rg.generate_roadmap("Data Analyst", "Beginner", 2, [])
        advanced = rg.generate_roadmap("Data Analyst", "Advanced", 2, [])
        self.assertLess(advanced["total_hours"], beginner["total_hours"])
        more_time = rg.generate_roadmap("Data Analyst", "Beginner", 4, [])
        self.assertEqual(more_time["total_hours"], beginner["total_hours"])
        self.assertLess(more_time["total_weeks"], beginner["total_weeks"])

    def test_core_only_is_shorter_than_with_bonus(self):
        full = rg.generate_roadmap("Frontend Developer", "Beginner", 2, [], include_bonus=True)
        core = rg.generate_roadmap("Frontend Developer", "Beginner", 2, [], include_bonus=False)
        self.assertLess(core["missing_count"], full["missing_count"])
        self.assertTrue(all(s["priority"] == "core" for st in core["stages"] for s in st["skills"]))

    def test_stage_weeks_follow_on_from_each_other(self):
        plan = rg.generate_roadmap("Backend Developer", "Beginner", 2, [], today=date(2026, 1, 1))
        with_skills = [st for st in plan["stages"] if st["skills"]]
        self.assertEqual(with_skills[0]["start_week"], 1)
        self.assertEqual(with_skills[-1]["end_week"], plan["total_weeks"])
        self.assertEqual(plan["total_hours"], sum(st["hours"] for st in plan["stages"]))

    def test_prerequisite_inference_and_free_text_skills(self):
        known, unknown = rg.normalize_skills(["Django"], "js, reactjs, Git & GitHub, not-a-skill")
        self.assertTrue({"JavaScript", "React", "Git", "GitHub"} <= known)
        self.assertEqual(unknown, ["not-a-skill"])
        everything, inferred = rg.expand_known({"Django", "React"})
        self.assertEqual(inferred["Python"], "Django")
        self.assertIn("HTML", everything)

    def test_resources_are_ordered_for_the_level(self):
        self.assertNotEqual(rg.skill_resources("JavaScript", "Beginner")[0]["title"],
                            rg.skill_resources("JavaScript", "Advanced")[0]["title"])
        for level in LEVELS:
            self.assertTrue(rg.skill_resources("Python", level))

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            rg.generate_roadmap("Astronaut", "Beginner", 2, [])
        with self.assertRaises(ValueError):
            rg.generate_roadmap("Backend Developer", "Beginner", 0, [])

    def test_progress_percentage(self):
        plan = rg.generate_roadmap("Backend Developer", "Beginner", 2, [])
        names = [s["name"] for st in plan["stages"] for s in st["skills"]]
        self.assertEqual(rg.progress_summary(plan, set())["pct"], 0)
        half = rg.progress_summary(plan, set(names[: len(names) // 2]))
        self.assertEqual(half["pct"], round(100 * (len(names) // 2) / len(names)))
        self.assertEqual(rg.progress_summary(plan, set(names))["pct"], 100)
        self.assertIsNone(rg.progress_summary(plan, set(names))["next"])
        self.assertEqual(rg.progress_summary(plan, {"Python"})["next"]["skill"], "Git")  # first not completed


class RoadmapPersistenceTests(unittest.TestCase):
    def test_save_track_regenerate(self):
        plan = rg.generate_roadmap("Backend Developer", "Beginner", 2, ["Python"])
        rid = repo.replace_roadmap(plan, ["Python"], True)
        self.assertEqual(repo.get_latest()["id"], rid)
        repo.set_completed(rid, "Git", True)
        repo.set_completed(rid, "Git", True)  # idempotent
        repo.set_completed(rid, "Linux", True)
        repo.set_completed(rid, "Linux", False)
        self.assertEqual(repo.completed_skills(rid), {"Git"})
        # regenerate: completed skills are carried over, the old roadmap and its progress are replaced
        new_plan = rg.generate_roadmap("Backend Developer", "Intermediate", 3, ["Python"], extra_known={"Git"})
        new_id = repo.replace_roadmap(new_plan, ["Git", "Python"], True)
        self.assertNotEqual(new_id, rid)
        self.assertEqual(repo.completed_skills(rid), set())
        latest = repo.get_latest()
        self.assertEqual((latest["plan"]["level"], latest["plan"]["hours_per_day"]), ("Intermediate", 3))
        self.assertNotIn("Git", [s["name"] for st in latest["plan"]["stages"] for s in st["skills"]])


if __name__ == "__main__":
    unittest.main()
