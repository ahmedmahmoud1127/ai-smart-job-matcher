"""Run from the project folder:  python -m unittest tests.test_skill_gap -v"""
import sys
import tempfile
import types
import unittest
from pathlib import Path

import database.db as dbm
from data.roadmaps import CAREER_ROADMAPS
from data.skill_gap_requirements import CAREER_REQUIREMENTS, COMPLEXITY_HOURS, LEVEL_RANK

dbm.DB_PATH = Path(tempfile.mkdtemp()) / "test_skill_gap.db"  # never touch the real database
dbm.init_db()

from database import roadmap_repository as roadmap_repo  # noqa: E402
from database import skill_gap_repository as repo  # noqa: E402
from services import skill_gap as sg  # noqa: E402


def U(*pairs):
    return [{"name": n, "level": l, "source": "test"} for n, l in pairs]


FULL_BACKEND = U(("Python", "Advanced"), ("Data Structures", "Advanced"), ("OOP", "Advanced"), ("Git", "Advanced"), ("Linux", "Advanced"),
                 ("Problem Solving", "Advanced"), ("SQL", "Advanced"), ("Database Optimization", "Advanced"), ("Django", "Advanced"),
                 ("APIs", "Advanced"), ("Authentication", "Advanced"), ("pytest", "Advanced"), ("System Design", "Advanced"),
                 ("Design Patterns", "Advanced"), ("Docker", "Advanced"), ("AWS", "Advanced"), ("CI/CD", "Advanced"), ("Redis", "Advanced"))


class DataTests(unittest.TestCase):
    def test_careers_match_the_roadmap_feature(self):
        self.assertEqual(set(CAREER_REQUIREMENTS), set(CAREER_ROADMAPS))

    def test_every_career_is_well_formed(self):
        for career, spec in CAREER_REQUIREMENTS.items():
            names = [r["name"] for r in spec["requirements"]]
            self.assertEqual(len(names), len(set(names)), career)
            self.assertEqual({r["stage"] for r in spec["requirements"]}, {1, 2, 3}, career)
            self.assertEqual(len(spec["stage_names"]), 3)
            for r in spec["requirements"]:
                self.assertIn(r["complexity"], COMPLEXITY_HOURS)
                self.assertIn(r["weight"], (1, 2, 3))
                self.assertIn(r["needs"], LEVEL_RANK)
                self.assertTrue(r["skills"])
                for dep in r["requires"]:
                    self.assertIn(dep, names, f"{career}: {r['name']} requires unknown {dep}")


class AnalysisTests(unittest.TestCase):
    def test_complete_profile_gives_100_percent_and_no_gap(self):
        r = sg.analyze("Backend Developer", FULL_BACKEND, "Intermediate", 2)
        self.assertEqual((r["match_pct"], r["need"], r["have"]), (100, 0, r["total"]))
        self.assertEqual(r["total_weeks"], 0)
        self.assertEqual(r["missing"], [])
        self.assertIn("cover every", r["recommendations"][0]["title"])

    def test_no_skills_gives_zero_percent(self):
        r = sg.analyze("Backend Developer", [], "Beginner", 2)
        self.assertEqual((r["match_pct"], r["have"], r["need"]), (0, 0, r["total"]))

    def test_aliases_and_levels(self):
        r = sg.analyze("Backend Developer", U(("Python", "Advanced"), ("APIs", "Intermediate"), ("SQL", "Intermediate"), ("OOP", "Beginner")), "Intermediate", 2)
        status = {i["name"]: i["status"] for i in r["requirements"]}
        self.assertEqual(status["REST APIs"], "have")              # 'APIs' counts as REST APIs
        self.assertEqual(status["Advanced Python"], "have")
        self.assertEqual(status["SQL"], "have")
        self.assertEqual(status["Advanced SQL"], "partial")        # knows SQL, but not at Advanced level
        self.assertEqual(status["OOP Principles"], "partial")      # Beginner vs Intermediate needed
        self.assertEqual(status["Docker"], "missing")

    def test_js_shorthand_and_implied_prerequisites(self):
        r = sg.analyze("Frontend Developer", U(("js", "Advanced"), ("React", "Intermediate")), "Intermediate", 2)
        status = {i["name"]: i["status"] for i in r["requirements"]}
        self.assertEqual(status["JavaScript"], "have")
        self.assertEqual(status["HTML"], "have")                   # React implies HTML
        r2 = sg.analyze("Backend Developer", U(("Django", "Advanced")), "Intermediate", 2)
        self.assertEqual({i["name"]: i["status"] for i in r2["requirements"]}["Python"], "have")   # Django implies Python

    def test_percentage_is_importance_weighted(self):
        r = sg.analyze("Backend Developer", U(("Python", "Advanced")), "Intermediate", 2)
        reqs = CAREER_REQUIREMENTS["Backend Developer"]["requirements"]
        got = sum(q["weight"] for q in reqs if q["name"] in ("Python", "Advanced Python"))
        self.assertEqual(r["match_pct"], round(100 * got / sum(q["weight"] for q in reqs)))

    def test_adding_a_skill_raises_the_match_and_removes_it_from_missing(self):
        base = U(("Python", "Intermediate"))
        before = sg.analyze("Backend Developer", base, "Intermediate", 2)
        after = sg.analyze("Backend Developer", base + U(("Docker", "Intermediate")), "Intermediate", 2)
        self.assertGreater(after["match_pct"], before["match_pct"])
        self.assertIn("Docker", [i["name"] for i in before["missing"]])
        self.assertNotIn("Docker", [i["name"] for i in after["missing"]])

    def test_missing_skills_are_categorised(self):
        r = sg.analyze("Backend Developer", U(("Python", "Advanced")), "Intermediate", 2)
        self.assertEqual(sum(len(v) for v in r["missing_groups"].values()), len(r["missing"]))
        self.assertIn("DevOps & Cloud", r["missing_groups"])

    def test_three_stages_with_week_ranges(self):
        r = sg.analyze("Backend Developer", U(("Python", "Intermediate")), "Intermediate", 2)
        self.assertEqual(len(r["stages"]), 3)
        weeks = [(s["start_week"], s["end_week"]) for s in r["stages"] if s["items"]]
        self.assertEqual(weeks[0][0], 1)
        for (a, b), (c, d) in zip(weeks, weeks[1:]):
            self.assertLessEqual(b, c)                             # stages follow each other
        self.assertEqual(r["stages"][-1]["end_week"], r["total_weeks"])


class DurationTests(unittest.TestCase):
    SK = U(("Python", "Intermediate"))

    def test_more_study_hours_means_fewer_weeks(self):
        slow, fast = (sg.analyze("Backend Developer", self.SK, "Intermediate", h)["total_weeks"] for h in (1, 4))
        self.assertGreater(slow, fast)

    def test_experience_level_changes_hours(self):
        hours = [sg.analyze("Backend Developer", self.SK, lv, 2)["total_hours"] for lv in ("Beginner", "Intermediate", "Advanced")]
        self.assertGreater(hours[0], hours[1])
        self.assertGreater(hours[1], hours[2])

    def test_complex_skills_take_longer(self):
        r = sg.analyze("Backend Developer", [], "Beginner", 2)
        by = {i["name"]: i["hours"] for i in r["requirements"]}
        self.assertGreater(by["System Design"], by["Git & GitHub"])

    def test_duration_label(self):
        self.assertEqual(sg.duration_label(0), "Done")
        self.assertEqual(sg.duration_label(3), "3 weeks")
        self.assertRegex(sg.duration_label(26), r"\d+–\d+ Months|\d+ Months?")

    def test_invalid_input_is_rejected(self):
        for args in (("Nope", [], "Beginner", 2), ("Backend Developer", [], "Expert", 2), ("Backend Developer", [], "Beginner", 0)):
            with self.assertRaises(ValueError):
                sg.analyze(*args)


class RecommendationTests(unittest.TestCase):
    def test_up_to_three_and_based_on_missing_skills(self):
        r = sg.analyze("Backend Developer", U(("Python", "Advanced"), ("SQL", "Intermediate")), "Intermediate", 2)
        self.assertEqual(len(r["recommendations"]), 3)
        missing = {i["name"] for i in r["missing"]}
        for rec in r["recommendations"]:
            self.assertIn(rec["skill"], missing)

    def test_recommendations_change_with_skills(self):
        a = sg.analyze("Backend Developer", U(("Python", "Advanced")), "Intermediate", 2)["recommendations"][0]["skill"]
        b = sg.analyze("Backend Developer", U(("Python", "Advanced"), (a, "Advanced")), "Intermediate", 2)["recommendations"][0]["skill"]
        self.assertNotEqual(a, b)

    def test_focus_modes_reorder(self):
        sk = U(("Python", "Intermediate"))
        quick = sg.analyze("Backend Developer", sk, "Intermediate", 2, "Quick wins")["missing"][0]
        impact = sg.analyze("Backend Developer", sk, "Intermediate", 2, "Highest impact")["missing"][0]
        self.assertLessEqual(quick["hours"], impact["hours"])

    def test_effective_skills_add_remove(self):
        out = sg.effective_skills(U(("Python", "Advanced"), ("Git", "Beginner")), {"Docker": "Intermediate", "git": "Advanced"}, ["Python"])
        self.assertEqual({s["name"].lower(): s["level"] for s in out}, {"git": "Advanced", "docker": "Intermediate"})

    def test_clean_skill_name(self):
        self.assertEqual(sg.clean_skill_name("js"), "JavaScript")
        self.assertEqual(sg.clean_skill_name("  Design   Patterns "), "Design Patterns")


class PersistenceTests(unittest.TestCase):
    def test_state_roundtrip_and_result_snapshot(self):
        with dbm.get_connection() as c:
            c.execute("DELETE FROM skill_gap_state")
        self.assertIsNone(repo.get_state())
        repo.save_state("Data Analyst", "Advanced", 3.5, "Quick wins", {"Docker": "Beginner"}, ["Linux"])
        s = repo.get_state()
        self.assertEqual((s["career"], s["level"], s["hours_per_day"], s["focus"], s["added"], s["removed"]),
                         ("Data Analyst", "Advanced", 3.5, "Quick wins", {"Docker": "Beginner"}, ["Linux"]))
        r = sg.analyze("Data Analyst", U(("SQL", "Advanced")), "Advanced", 3.5)
        repo.save_result(sg.summary(r))
        s = repo.get_state()
        self.assertEqual(s["result"]["match_pct"], r["match_pct"])
        self.assertTrue(s["generated_at"])
        repo.save_state("Backend Developer", "Beginner", 1.0, "Balanced", {}, [])     # update, no duplicate row
        self.assertEqual(repo.get_state()["career"], "Backend Developer")


class HandOffTests(unittest.TestCase):
    """start_learning_plan with a tiny fake `streamlit` (the real UI needs a browser)."""

    def setUp(self):
        class SS(dict):
            __getattr__ = dict.get
            __setattr__ = dict.__setitem__
        self.ss = SS()
        fake = types.SimpleNamespace(session_state=self.ss)
        self._saved = {k: sys.modules.get(k) for k in ("streamlit", "plotly", "plotly.graph_objects")}
        sys.modules["streamlit"] = fake
        for k in [m for m in sys.modules if m.startswith("components.")]:
            del sys.modules[k]
        repo.save_state("Backend Developer", "Intermediate", 2.0, "Balanced", {"Docker": "Intermediate"}, [])
        roadmap_repo.delete_roadmap()

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        for k in [m for m in sys.modules if m.startswith("components.")]:
            del sys.modules[k]

    def test_creates_roadmap_navigates_and_keeps_existing_progress(self):
        from components.skill_gap import state as S
        S.start_learning_plan()
        self.assertEqual(self.ss["page"], "Learning Roadmap")
        latest = roadmap_repo.get_latest()
        self.assertEqual(latest["plan"]["career"], "Backend Developer")
        self.assertIn("Docker", latest["selected_skills"])               # the skill added here is known in the roadmap
        rid = latest["id"]
        roadmap_repo.set_completed(rid, "Python", True)
        self.ss["page"] = "Skill Gap Analysis"
        S.start_learning_plan()                                         # same career: nothing is overwritten
        self.assertEqual(roadmap_repo.get_latest()["id"], rid)
        self.assertEqual(roadmap_repo.completed_skills(rid), {"Python"})

    def test_different_career_only_prefills_the_form(self):
        from components.skill_gap import state as S
        S.start_learning_plan()
        rid = roadmap_repo.get_latest()["id"]
        repo.save_state("Data Analyst", "Beginner", 1.5, "Balanced", {}, [])
        S.start_learning_plan()
        self.assertEqual(roadmap_repo.get_latest()["id"], rid)           # current roadmap untouched
        self.assertEqual((self.ss["rm_career"], self.ss["rm_level"], self.ss["rm_hours"]), ("Data Analyst", "Beginner", 1.5))


if __name__ == "__main__":
    unittest.main()
