"""Skill Gap Analysis: plain Python rules over predefined career requirements (data/skill_gap_requirements.py).

No NLP, computer vision, machine learning or external AI API is used. Steps:
  1. normalise the user's skills (existing alias dictionary + prerequisite inference, e.g. Django -> Python),
  2. compare them with every requirement of the target career (credit 1.0 / 0.5 / 0.25 / 0 depending on the level),
  3. match % = importance-weighted credit; "have" = fully satisfied, "need" = partial or missing,
  4. study hours = complexity hours x experience-level factor x share still missing, converted to weeks with the daily hours,
  5. build 3 learning stages and 3 recommendations from the missing skills.
"""
from __future__ import annotations

import math
from typing import Optional

from data.roadmaps import IMPLIES, LEVEL_FACTOR, LEVELS, STUDY_DAYS_PER_WEEK
from data.skill_gap_requirements import (CAREER_REQUIREMENTS, CAREERS, COMPLEXITY_HOURS, FOCUS_MODES, IMPORTANCE, LEVEL_RANK,
                                         STAGE_COLORS)
from data.skills_catalog import SKILL_CATEGORY
from services.roadmap_generator import normalize_skills

_LOWER_TO_CANON = {s.lower(): s for s in SKILL_CATEGORY}
PARTIAL_CREDIT = {1: 0.5, 2: 0.25}   # credit when the skill is known 1 or 2 levels below what the job needs


def careers() -> list:
    return list(CAREERS)


def career_category(career: str) -> str:
    return CAREER_REQUIREMENTS[career]["category"]


# ------------------------------------------------------------------------------------ the user's skills
def default_level(credit: float) -> str:
    """Map the proficiency credit used by Smart Job Matching back to a level."""
    return "Advanced" if credit >= 0.95 else "Intermediate" if credit >= 0.75 else "Beginner"


def collect_project_skills() -> list:
    """Skills known from My Profile, the CV Analyzer, projects and experience (same source as Smart Job Matching)."""
    from services.job_matching import build_candidate  # imported here to keep this module light and testable
    out = []
    for name, info in build_candidate()["skills"].items():
        out.append({"name": name, "level": default_level(info["credit"]), "source": info["sources"][0] if info["sources"] else ""})
    return sorted(out, key=lambda s: s["name"].lower())


def effective_skills(base: list, added: dict, removed: list) -> list:
    """base skills minus the removed ones plus the added ones (an added skill overrides the level of a base skill)."""
    gone = {r.lower() for r in removed}
    result = {s["name"].lower(): dict(s) for s in base if s["name"].lower() not in gone}
    for name, level in added.items():
        result[name.lower()] = {"name": name, "level": level, "source": "Added here"}
    return sorted(result.values(), key=lambda s: s["name"].lower())


def clean_skill_name(raw: str) -> str:
    """Canonical catalogue name when the text is a known skill/alias (e.g. 'js' -> 'JavaScript'), else the tidy text."""
    text = " ".join((raw or "").split())
    known, _ = normalize_skills([], text)
    if len(known) == 1:
        return next(iter(known))
    return _LOWER_TO_CANON.get(text.lower(), text)


def _ranks(skills: list) -> dict:
    """lower-case skill token -> best level rank, including prerequisites implied by known skills."""
    ranks: dict = {}

    def put(token: str, rank: int) -> None:
        if rank > ranks.get(token, -1):
            ranks[token] = rank

    for s in skills:
        rank = LEVEL_RANK.get(s["level"], 1)
        known, _ = normalize_skills([], s["name"])
        for token in {s["name"].strip().lower()} | {k.lower() for k in known}:
            put(token, rank)
    for _ in range(3):  # prerequisite inference, e.g. Django -> Python (capped at Intermediate)
        for implier, implied in IMPLIES.items():
            if implier.lower() in ranks:
                for imp in implied:
                    put(imp.lower(), min(ranks[implier.lower()], 1))
    return ranks


# ------------------------------------------------------------------------------------ analysis
def duration_label(weeks: int) -> str:
    if weeks <= 0:
        return "Done"
    if weeks <= 4:
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    months = weeks / 4.33
    low, high = max(1, round(months * 0.85)), max(1, math.ceil(months * 1.15))
    high = max(low, high)
    return f"{low} Month{'s' if low != 1 else ''}" if low == high else f"{low}–{high} Months"


def _credit(req: dict, ranks: dict) -> tuple:
    """(credit, user's level rank or None) for one requirement."""
    have = max((ranks[t] for t in req["skills"] if t in ranks), default=None)
    if have is None:
        return 0.0, None
    gap = LEVEL_RANK[req["needs"]] - have
    return (1.0 if gap <= 0 else PARTIAL_CREDIT.get(gap, 0.25)), have


def _priority(req: dict, credit: float, hours: int, ready: bool, focus: str) -> float:
    w, cx = req["weight"], req["complexity"]
    if focus == "Quick wins":
        return w * 1.5 - hours / 12 + (2 if ready else 0)
    if focus == "Highest impact":
        return w * 5 + (1 - credit) * 2 + (1 if ready else 0)
    return w * 3 + (2 if ready else 0) - cx * 0.4 + (1 - credit) - req["stage"] * 0.8  # earlier stages come first


def analyze(career: str, skills: list, level: str = "Intermediate", hours_per_day: float = 2.0, focus: str = "Balanced") -> dict:
    if career not in CAREER_REQUIREMENTS:
        raise ValueError(f"Unknown career: {career}")
    if level not in LEVELS:
        raise ValueError(f"Unknown level: {level}")
    if hours_per_day <= 0:
        raise ValueError("Study hours per day must be greater than zero")
    if focus not in FOCUS_MODES:
        raise ValueError(f"Unknown focus: {focus}")
    spec, ranks = CAREER_REQUIREMENTS[career], _ranks(skills)
    reqs = spec["requirements"]
    credits = {r["name"]: _credit(r, ranks) for r in reqs}
    rank_names = {v: k for k, v in LEVEL_RANK.items()}

    items = []
    for r in reqs:
        credit, have = credits[r["name"]]
        status = "have" if credit >= 1 else "partial" if credit > 0 else "missing"
        hours = 0 if status == "have" else max(2, round(COMPLEXITY_HOURS[r["complexity"]] * LEVEL_FACTOR[level] * (1 - credit)))
        ready = all(credits.get(p, (1.0, 0))[0] >= 1 for p in r["requires"])
        items.append({**{k: r[k] for k in ("name", "category", "weight", "complexity", "stage", "purpose", "needs", "requires")},
                      "status": status, "credit": credit, "hours": hours, "ready": ready,
                      "importance": IMPORTANCE[r["weight"]], "user_level": rank_names.get(have, "") if have is not None else "",
                      "priority": round(_priority(r, credit, hours, ready, focus), 3)})

    total_w = sum(i["weight"] for i in items)
    match_pct = round(100 * sum(i["weight"] * i["credit"] for i in items) / total_w) if total_w else 0
    have_n = sum(i["status"] == "have" for i in items)
    todo = sorted((i for i in items if i["status"] != "have"), key=lambda i: (-i["priority"], i["stage"], i["name"]))

    weekly = hours_per_day * STUDY_DAYS_PER_WEEK
    stages, cumulative = [], 0
    for idx, name in enumerate(spec["stage_names"], start=1):
        in_stage = [i for i in items if i["stage"] == idx]
        work = sorted((i for i in in_stage if i["status"] != "have"), key=lambda i: (0 if i["ready"] else 1, -i["priority"], i["name"]))
        hours = sum(i["hours"] for i in work)
        stage = {"index": idx, "name": name, "color": STAGE_COLORS[idx], "items": work,
                 "known": [i["name"] for i in in_stage if i["status"] == "have"], "total": len(in_stage), "hours": hours,
                 "progress_pct": round(100 * sum(i["credit"] for i in in_stage) / len(in_stage)) if in_stage else 100,
                 "start_week": None, "end_week": None, "weeks": 0}
        if work:
            stage["start_week"] = int(cumulative // weekly) + 1
            stage["end_week"] = max(stage["start_week"], math.ceil((cumulative + hours) / weekly))
            stage["weeks"] = max(1, math.ceil(hours / weekly))
            cumulative += hours
        stage["duration"] = duration_label(stage["weeks"]) if work else "Completed"
        stages.append(stage)
    total_weeks = math.ceil(cumulative / weekly) if cumulative else 0

    groups: dict = {}
    for i in todo:
        groups.setdefault(i["category"], []).append(i)
    coverage: dict = {}
    for i in items:
        c = coverage.setdefault(i["category"], {"credit": 0.0, "n": 0})
        c["credit"] += i["credit"]
        c["n"] += 1

    return {"career": career, "category": spec["category"], "level": level, "hours_per_day": hours_per_day, "focus": focus,
            "match_pct": match_pct, "have": have_n, "need": len(items) - have_n, "total": len(items),
            "missing_count": sum(i["status"] == "missing" for i in items), "partial_count": sum(i["status"] == "partial" for i in items),
            "requirements": items, "missing": todo, "missing_groups": groups,
            "category_coverage": {k: round(100 * v["credit"] / v["n"]) for k, v in coverage.items()},
            "stages": stages, "total_hours": cumulative, "total_weeks": total_weeks,
            "total_duration": duration_label(total_weeks), "recommendations": recommend(todo, level, career)}


# ------------------------------------------------------------------------------------ recommendations
def recommend(todo: list, level: str, career: str, limit: int = 3) -> list:
    """Up to 3 recommendations built from the missing skills: start with the top priority one, then a skill from another
    category, then practise a partially known skill (or the next missing one)."""
    if not todo:
        return [{"title": f"You cover every {career} requirement", "reason": "Apply for jobs or deepen your projects to stand out.",
                 "skill": "", "hours": 0}]
    ordered = list(todo)
    first = ordered.pop(0)
    recs = [{"title": f"Start with {first['name']}", "skill": first["name"], "hours": first["hours"],
             "reason": f"{first['importance']}-priority for {career}: needed for {first['purpose']}. About {first['hours']} h of study."
                       + ("" if first["ready"] else f" Learn {', '.join(first['requires'])} first.")}]
    second = next((i for i in ordered if i["category"] != first["category"] and i["status"] == "missing"), None) or \
        next((i for i in ordered if i["status"] == "missing"), None)
    if second:
        ordered.remove(second)
        recs.append({"title": f"Learn {second['name']} for {second['purpose']}", "skill": second["name"], "hours": second["hours"],
                     "reason": f"{second['importance']} priority, {second['category']}. About {second['hours']} h at {level} level."})
    third = next((i for i in ordered if i["status"] == "partial"), None) or (ordered[0] if ordered else None)
    if third and len(recs) < limit:
        if third["status"] == "partial":
            recs.append({"title": f"Practice more on {third['name']}", "skill": third["name"], "hours": third["hours"],
                         "reason": f"You know the basics ({third['user_level']}) but the role needs {third['needs']} level."})
        else:
            recs.append({"title": f"Next, learn {third['name']}", "skill": third["name"], "hours": third["hours"],
                         "reason": f"Needed for {third['purpose']}. About {third['hours']} h of study."})
    return recs[:limit]


# ------------------------------------------------------------------------------------ hand-off to Learning Roadmap
def catalog_skill_names(skills: list) -> list:
    """Skill names the Learning Roadmap understands (catalogue names), for pre-filling its form."""
    known, _ = normalize_skills([], ", ".join(s["name"] for s in skills))
    return sorted(known)


def summary(result: dict) -> dict:
    """Small JSON-friendly snapshot that is stored in SQLite."""
    return {k: result[k] for k in ("career", "level", "hours_per_day", "focus", "match_pct", "have", "need", "total",
                                   "total_hours", "total_weeks", "total_duration")} | {
        "missing": [i["name"] for i in result["missing"]], "recommendations": [r["title"] for r in result["recommendations"]],
        "stages": [{"name": s["name"], "duration": s["duration"], "skills": [i["name"] for i in s["items"]]} for s in result["stages"]]}
