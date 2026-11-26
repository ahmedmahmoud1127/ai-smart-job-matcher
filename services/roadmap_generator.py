"""Learning Roadmap generator: plain Python rules over predefined career roadmaps (data/roadmaps.py).

No NLP, computer vision, machine learning or external API is involved. The steps are:
  1. normalise the student's skills (dictionary / alias lookup, then prerequisite inference),
  2. compare them with the skills of the chosen career, stage by stage, to find what is missing,
  3. estimate hours per skill from a base table scaled by the experience level, then convert hours to days and weeks
     using the daily study hours,
  4. attach resources (ordered to suit the experience level) and a mini-project to every stage.
"""
from __future__ import annotations

import math
import re
from datetime import date, timedelta
from typing import Optional

from data.roadmaps import (CAREER_ROADMAPS, DEFAULT_SKILL_HOURS, IMPLIES, KIND_PREFERENCE, LEVEL_FACTOR, LEVELS, RESOURCES,
                           SKILL_HOURS, STUDY_DAYS_PER_WEEK)
from data.skills_catalog import SKILL_CATEGORY
from services.skills_extractor import canonical_names

MAX_RESOURCES = 3
_LOWER_TO_SKILL = {s.lower(): s for s in SKILL_CATEGORY}
SHORTHAND = {"js": "JavaScript", "ts": "TypeScript", "py": "Python", "reactjs": "React", "react.js": "React", "node": "Node.js",
             "nodejs": "Node.js", "vue": "Vue.js", "vuejs": "Vue.js", "postgres": "PostgreSQL", "k8s": "Kubernetes",
             "ml": "Machine Learning", "dl": "Deep Learning", "ci cd": "CI/CD", "cicd": "CI/CD", "excel": "Microsoft Excel",
             "tailwind": "Tailwind CSS", "express": "Express.js", "sklearn": "Scikit-learn", "tf": "TensorFlow"}


def careers() -> list:
    return list(CAREER_ROADMAPS)


# ------------------------------------------------------------------------------------ student skills
def normalize_skills(selected: list, extra_text: str = "") -> tuple:
    """Return (known skills, unrecognised words). `selected` are catalogue names; `extra_text` is free text such as
    'js, reactjs, Git & GitHub' which is matched against the skill aliases."""
    known = {s for s in selected if s in SKILL_CATEGORY}
    unknown = []
    for token in re.split(r"[,;\n]+", extra_text or ""):
        token = token.strip()
        if not token:
            continue
        key = token.lower()
        names = canonical_names(token) or ({_LOWER_TO_SKILL[key]} if key in _LOWER_TO_SKILL else {SHORTHAND[key]} if key in SHORTHAND else set())
        if names:
            known |= names
        else:
            unknown.append(token)
    return known, unknown


def expand_known(known: set) -> tuple:
    """Add prerequisite skills implied by what the student knows (e.g. Django -> Python).
    Returns (all known skills, {inferred skill: skill it was inferred from})."""
    all_known, inferred = set(known), {}
    changed = True
    while changed:
        changed = False
        for skill in sorted(all_known):
            for implied in IMPLIES.get(skill, ()):
                if implied not in all_known:
                    all_known.add(implied)
                    inferred[implied] = skill
                    changed = True
    return all_known, inferred


# ------------------------------------------------------------------------------------ plan building
def skill_hours(skill: str, level: str) -> int:
    return max(2, round(SKILL_HOURS.get(skill, DEFAULT_SKILL_HOURS) * LEVEL_FACTOR[level]))


def skill_resources(skill: str, level: str, limit: int = MAX_RESOURCES) -> list:
    """Resources for a skill, ordered so the kinds that suit the level come first (stable for ties)."""
    order = KIND_PREFERENCE[level]
    items = RESOURCES.get(skill) or [{"title": f"Search for a beginner {skill} course and build one small project with it",
                                      "provider": "Self-practice", "url": "", "kind": "Practice", "free": True}]
    ranked = sorted(enumerate(items), key=lambda p: (order.index(p[1]["kind"]) if p[1]["kind"] in order else len(order), p[0]))
    return [dict(item) for _, item in ranked[:limit]]


def format_duration(hours: float, hours_per_day: float) -> str:
    days = max(1, math.ceil(hours / hours_per_day))
    if days <= STUDY_DAYS_PER_WEEK:
        return f"{days} study day{'s' if days != 1 else ''}"
    weeks = days / STUDY_DAYS_PER_WEEK
    return f"≈ {weeks:.1f}".rstrip("0").rstrip(".") + " weeks"


def generate_roadmap(career: str, level: str, hours_per_day: float, selected_skills: list, *, include_bonus: bool = True,
                     extra_known: Optional[set] = None, today: Optional[date] = None) -> dict:
    """Build a personalised roadmap. `extra_known` are skills to count as known without being typed again
    (e.g. skills completed in the previous roadmap)."""
    if career not in CAREER_ROADMAPS:
        raise ValueError(f"Unknown career: {career}")
    if level not in LEVELS:
        raise ValueError(f"Unknown level: {level}")
    if hours_per_day <= 0:
        raise ValueError("Study hours per day must be greater than zero")
    today = today or date.today()
    explicit = set(selected_skills) | set(extra_known or ())
    all_known, inferred = expand_known(explicit)
    weekly_hours = hours_per_day * STUDY_DAYS_PER_WEEK

    stages, cumulative, career_skills, covered_total = [], 0, 0, 0
    for index, st in enumerate(CAREER_ROADMAPS[career]["stages"], start=1):
        wanted = [(s, "core") for s in st["core"]] + ([(s, "bonus") for s in st["bonus"]] if include_bonus else [])
        career_skills += len(wanted)
        covered = [s for s, _ in wanted if s in all_known]
        covered_total += len(covered)
        skills = []
        for name, priority in wanted:
            if name in all_known:
                continue
            h = skill_hours(name, level)
            skills.append({"name": name, "priority": priority, "hours": h, "days": math.ceil(h / hours_per_day),
                           "resources": skill_resources(name, level)})
        hours = sum(s["hours"] for s in skills)
        stage = {"index": index, "name": st["name"], "goal": st["goal"], "project": st["project"], "skills": skills,
                 "covered": covered, "hours": hours, "duration": format_duration(hours, hours_per_day) if hours else "",
                 "start_week": None, "end_week": None}
        if skills:
            stage["start_week"] = int(cumulative // weekly_hours) + 1
            stage["end_week"] = max(stage["start_week"], math.ceil((cumulative + hours) / weekly_hours))
            cumulative += hours
        stages.append(stage)

    total_weeks = math.ceil(cumulative / weekly_hours) if cumulative else 0
    return {"career": career, "summary": CAREER_ROADMAPS[career]["summary"], "level": level, "hours_per_day": hours_per_day,
            "study_days_per_week": STUDY_DAYS_PER_WEEK, "include_bonus": include_bonus,
            "known_skills": sorted(explicit), "inferred": inferred, "stages": stages,
            "missing_count": sum(len(s["skills"]) for s in stages), "career_skill_count": career_skills,
            "coverage_pct": round(100 * covered_total / career_skills) if career_skills else 0,
            "total_hours": cumulative, "total_weeks": total_weeks,
            "total_duration": format_duration(cumulative, hours_per_day) if cumulative else "",
            "generated_on": today.isoformat(),
            "finish_on": (today + timedelta(weeks=total_weeks)).isoformat() if total_weeks else today.isoformat()}


# ------------------------------------------------------------------------------------ progress
def progress_summary(plan: dict, completed: set) -> dict:
    """Completion numbers for the whole plan and for every stage. Only skills that are in the plan count."""
    per_stage, done_total, hours_done = [], 0, 0
    next_skill = None
    for st in plan["stages"]:
        names = [s["name"] for s in st["skills"]]
        done = sum(n in completed for n in names)
        done_total += done
        hours_done += sum(s["hours"] for s in st["skills"] if s["name"] in completed)
        status = "covered" if not names else "done" if done == len(names) else "doing" if done else "todo"
        per_stage.append({"index": st["index"], "done": done, "total": len(names), "status": status,
                          "pct": round(100 * done / len(names)) if names else 100})
        if next_skill is None:
            nxt = next((s for s in st["skills"] if s["name"] not in completed), None)
            if nxt:
                next_skill = {"skill": nxt["name"], "stage": st["name"], "hours": nxt["hours"]}
    total = plan["missing_count"]
    return {"done": done_total, "total": total, "pct": round(100 * done_total / total) if total else 100,
            "hours_done": hours_done, "hours_left": plan["total_hours"] - hours_done, "stages": per_stage, "next": next_skill}
