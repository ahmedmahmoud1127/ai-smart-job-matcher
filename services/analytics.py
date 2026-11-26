"""Analytics Dashboard calculations: plain Python over the data the app already stores.

No NLP, computer vision, machine learning or external AI API is used, and nothing is random or hard-coded.
Every number comes from one of these existing sources:

  * My Profile / projects / CV skills ........ services.job_matching.build_candidate (the same candidate Smart Job Matching uses)
  * Job match scores ......................... services.job_matching.rank_jobs / recommend_skills
  * Target career, readiness, missing skills . services.skill_gap.analyze (the user's saved Skill Gap settings)
  * Roadmap, progress and completion dates ... roadmap_repository + the `roadmap_progress` table
  * CV Analyzer history ...................... cv_repository
  * Day-by-day history ....................... `analytics_snapshots` (one row per day the dashboard was opened)

Learning hours are *estimated*: the app has no study timer, so a skill ticked off in the Learning Roadmap counts for the
hours the roadmap planned for that skill, on the day it was ticked. A statistic that cannot be computed is returned as
None (or an empty list) and the UI shows an empty state instead of a made-up value.

Two layers: `load_raw()` reads the database (side effect: stores today's snapshot) and `build_dashboard()` is a pure
function over that data, so it can be tested with small synthetic inputs.
"""
from __future__ import annotations

import math
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from data.skill_gap_requirements import CAREERS
from data.skills_catalog import SKILL_CATEGORY
from database import analytics_repository as repo
from database import cv_repository as cv_repo
from database import roadmap_repository as roadmap_repo
from database import skill_gap_repository as gap_repo
from database.session import resolve_user_id
from services import job_matching, profile_data, skill_gap
from services.roadmap_generator import progress_summary

WINDOWS = {"7 Days": 7, "30 Days": 30, "90 Days": 90, "All Time": None}
DEFAULT_WINDOW = "30 Days"

GROUPS = ["Programming Languages", "Frameworks & Web", "Data & AI", "Databases", "CS Fundamentals", "Tools & DevOps", "Soft Skills", "Other"]
CATALOG_GROUP = {"Programming Languages": "Programming Languages", "Web Development": "Frameworks & Web",
                 "Data Science": "Data & AI", "Databases": "Databases", "Tools & Technologies": "Tools & DevOps",
                 "Soft Skills": "Soft Skills"}
GAP_GROUP = {"Programming": "Programming Languages", "Web & APIs": "Frameworks & Web", "Data & AI": "Data & AI",
             "Databases": "Databases", "CS Fundamentals": "CS Fundamentals", "Tools": "Tools & DevOps", "DevOps & Cloud": "Tools & DevOps",
             "Security": "Tools & DevOps", "Soft Skills": "Soft Skills"}
SCORE_BANDS = [("Excellent", 80, 101), ("Strong", 65, 80), ("Good", 50, 65), ("Partial", 35, 50), ("Low", 0, 35)]
TOP_JOBS_FOR_SKILLS = 10   # "most requested skills" are counted over the user's closest-fitting jobs
MIN_HEATMAP_WEEKS, MAX_HEATMAP_WEEKS = 4, 26


# ------------------------------------------------------------------------------------------ small helpers
def group_of_skill(name: str) -> str:
    return CATALOG_GROUP.get(SKILL_CATEGORY.get(name, ""), "Other")


def group_of_gap(category: str) -> str:
    return GAP_GROUP.get(category, "Other")


def to_local_date(timestamp: str) -> Optional[date]:
    """SQLite CURRENT_TIMESTAMP is UTC ('YYYY-MM-DD HH:MM:SS'); convert it to the local calendar day."""
    try:
        dt = datetime.fromisoformat(str(timestamp).replace("T", " ")[:19])
    except ValueError:
        return None
    return dt.replace(tzinfo=timezone.utc).astimezone().date()


def _pct(part: float, whole: float) -> int:
    return int(round(100 * part / whole)) if whole else 0


def _avg(values: list) -> Optional[float]:
    return round(sum(values) / len(values), 1) if values else None


def _hours(value: float) -> float:
    return round(value, 1)


def _delta(now: Optional[float], before: Optional[float]) -> Optional[float]:
    return None if now is None or before is None else round(now - before, 1)


# ------------------------------------------------------------------------------------------ loading
def _target_career(state: Optional[dict], roadmap: Optional[dict], prefs: dict) -> Optional[str]:
    """Saved Skill Gap career first, then the roadmap's career, then the career chosen in My Profile. Never guessed."""
    if state and state["career"] in CAREERS:
        return state["career"]
    if roadmap and roadmap["plan"]["career"] in CAREERS:
        return roadmap["plan"]["career"]
    role = prefs.get("effective_role")
    return role if role in CAREERS else None


def _gap_analysis(cand: dict, state: Optional[dict], career: Optional[str]) -> Optional[dict]:
    if not career:
        return None
    base = [{"name": n, "level": skill_gap.default_level(i["credit"]), "source": (i["sources"] or [""])[0]}
            for n, i in cand["skills"].items()]
    base.sort(key=lambda s: s["name"].lower())
    skills = skill_gap.effective_skills(base, state["added"], state["removed"]) if state else base
    level = state["level"] if state else "Intermediate"
    hours = float(state["hours_per_day"]) if state else 2.0
    focus = state["focus"] if state else "Balanced"
    return skill_gap.analyze(career, skills, level, hours, focus)


def snapshot_values(raw: dict) -> dict:
    """The numbers stored once per day so progress over time can be charted."""
    results, gap, cv = raw["results"], raw["gap"], raw["cv_latest"]
    scores = [r["score"] for r in results]
    plan_total = raw["progress"]["total"] if raw["progress"] else None
    return {"readiness": gap["match_pct"] if gap else None,
            "avg_match": _avg(scores), "best_match": max(scores) if scores else None,
            "strong_matches": sum(s >= job_matching.UNLOCK_AT for s in scores) if scores else None,
            "top5_avg": _avg(scores[:5]), "jobs_analyzed": len(scores) or None,
            "skills_count": len(raw["cand"]["skills"]), "cv_score": cv["score"] if cv else None,
            "roadmap_pct": raw["progress"]["pct"] if plan_total else None}


def load_raw(user_id: int | None = None, today: Optional[date] = None, record: bool = True) -> dict:
    """Read everything the dashboard needs. With record=True today's snapshot is stored (one row per day)."""
    user_id = resolve_user_id(user_id)
    today = today or date.today()
    profile = profile_data.get_full_profile(user_id)
    cand = job_matching.build_candidate(user_id, today)
    results = job_matching.rank_jobs(cand)
    recs = job_matching.recommend_skills(cand, results, limit=3) if cand["skills"] else {"skills": [], "projection": None}

    state = gap_repo.get_state(user_id)
    latest = roadmap_repo.get_latest(user_id)
    career = _target_career(state, latest, profile["preferences"])
    gap = _gap_analysis(cand, state, career)

    plan, events, progress = None, [], None
    if latest:
        plan = latest["plan"]
        done_names = roadmap_repo.completed_skills(latest["id"])
        progress = progress_summary(plan, done_names)
        info = {s["name"]: {**s, "stage": st["name"], "stage_index": st["index"]} for st in plan["stages"] for s in st["skills"]}
        for e in repo.completed_events(latest["id"]):
            d, meta = to_local_date(e["completed_at"]), info.get(e["skill"])
            if d and meta:
                events.append({"skill": e["skill"], "date": d, "hours": meta["hours"], "stage": meta["stage"],
                               "group": group_of_skill(e["skill"])})

    analyses = cv_repo.list_analyses(user_id)  # newest first
    for a in analyses:
        a["date"] = to_local_date(a["created_at"])
    cv_latest = None
    if analyses:
        full = cv_repo.get_analysis(analyses[0]["id"], user_id)
        res = full["result"]
        kw = res.get("keywords", {})
        cv_latest = {"id": full["id"], "file_name": full["file_name"], "role": res.get("role", full["target_role"]),
                     "score": full["score"], "label": res.get("score", {}).get("label", ""),
                     "breakdown": res.get("score", {}).get("breakdown", {}), "date": analyses[0]["date"],
                     "skills": [s["name"] for s in res.get("skills", [])],
                     "missing": list(kw.get("missing_required", [])) + list(kw.get("missing_preferred", []))}

    raw = {"today": today, "first_name": (profile["user"].get("full_name") or "").split(" ")[0] or "there",
           "cand": cand, "results": results, "recs": recs, "state": state, "career": career, "gap": gap,
           "roadmap": latest, "plan": plan, "progress": progress, "events": events,
           "analyses": analyses, "cv_latest": cv_latest, "snapshots": []}
    if record:
        repo.save_snapshot(today.isoformat(), snapshot_values(raw), user_id)
    raw["snapshots"] = repo.list_snapshots(user_id)
    return raw


# ------------------------------------------------------------------------------------------ learning activity
def _window_bounds(days: Optional[int], today: date, first: Optional[date]) -> tuple:
    """(start, previous_start, previous_end) of the selected period. All Time starts at the first recorded activity."""
    if days:
        start = today - timedelta(days=days - 1)
        return start, start - timedelta(days=days), start - timedelta(days=1)
    return first, None, None


def _streak(active: set, today: date) -> int:
    day = today if today in active else today - timedelta(days=1)
    n = 0
    while day in active:
        n += 1
        day -= timedelta(days=1)
    return n


def _heatmap(by_day: dict, today: date, weeks: int) -> dict:
    """Columns = weeks (Monday first), rows = Mon..Sun. Future days are None."""
    monday = today - timedelta(days=today.weekday())
    first_monday = monday - timedelta(weeks=weeks - 1)
    z, text = [[None] * weeks for _ in range(7)], [[""] * weeks for _ in range(7)]
    for w in range(weeks):
        for d in range(7):
            day = first_monday + timedelta(weeks=w, days=d)
            if day > today:
                continue
            h = by_day.get(day, 0.0)
            z[d][w] = _hours(h)
            text[d][w] = day.strftime("%a %d %b %Y")
    return {"weeks": [(first_monday + timedelta(weeks=w)).strftime("%d %b") for w in range(weeks)],
            "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "z": z, "text": text,
            "max": max([v for row in z for v in row if v is not None] or [0])}


def learning_activity(raw: dict, days: Optional[int]) -> dict:
    today, events = raw["today"], raw["events"]
    by_day, tasks_day, skills_day = Counter(), Counter(), {}
    for e in events:
        by_day[e["date"]] += e["hours"]
        tasks_day[e["date"]] += 1
        skills_day.setdefault(e["date"], []).append(e["skill"])
    first = min(by_day) if by_day else None
    start, prev_start, prev_end = _window_bounds(days, today, first)

    def hours_between(a: date, b: date) -> float:
        return sum(h for d, h in by_day.items() if a <= d <= b)

    in_window = lambda d: start is None or start <= d <= today
    window_hours = _hours(sum(h for d, h in by_day.items() if in_window(d)))
    window_tasks = sum(n for d, n in tasks_day.items() if in_window(d))
    prev_hours = _hours(hours_between(prev_start, prev_end)) if prev_start else None
    prev_tasks = sum(n for d, n in tasks_day.items() if prev_start <= d <= prev_end) if prev_start else None

    span = days if days else ((today - first).days + 1 if first else 0)
    active = {d for d in by_day if in_window(d)}
    consistency = _pct(len(active), span) if span and by_day else None

    week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    weekly = [{"date": d, "label": d.strftime("%a"), "full": d.strftime("%A %d %b"), "hours": _hours(by_day.get(d, 0.0)),
               "tasks": tasks_day.get(d, 0), "skills": skills_day.get(d, [])} for d in week]
    this_week = _hours(sum(w["hours"] for w in weekly))
    last_week = _hours(hours_between(today - timedelta(days=13), today - timedelta(days=7)))

    if days:
        weeks = math.ceil(days / 7)
    else:
        weeks = math.ceil(((today - first).days + 1) / 7) if first else MIN_HEATMAP_WEEKS
    weeks = max(MIN_HEATMAP_WEEKS, min(MAX_HEATMAP_WEEKS, weeks))
    return {"has_data": bool(events), "first_date": first, "today_hours": _hours(by_day.get(today, 0.0)),
            "week_hours": this_week, "last_week_hours": last_week, "month_hours": _hours(hours_between(today - timedelta(days=29), today)),
            "window_hours": window_hours, "prev_hours": prev_hours, "window_tasks": window_tasks, "prev_tasks": prev_tasks,
            "total_tasks": len(events), "total_hours": _hours(sum(by_day.values())), "active_days": len(active),
            "consistency": consistency, "streak": _streak(set(by_day), today), "span_days": span,
            "weekly": weekly, "heatmap": _heatmap(by_day, today, weeks),
            "best_day": (max(weekly, key=lambda w: w["hours"]) if any(w["hours"] for w in weekly) else None)}


# ------------------------------------------------------------------------------------------ skills
def skills_analytics(raw: dict, days: Optional[int]) -> dict:
    today, events, gap, cand = raw["today"], raw["events"], raw["gap"], raw["cand"]
    start = today - timedelta(days=days - 1) if days else None
    acquired = [e for e in events if start is None or e["date"] >= start]
    acquired_all = [e for e in events]

    current = [{"name": n, "group": group_of_skill(n), "credit": i["credit"], "sources": i["sources"]}
               for n, i in sorted(cand["skills"].items())]
    missing = [{"name": m["name"], "group": group_of_gap(m["category"]), "importance": m["importance"], "status": m["status"],
                "hours": m["hours"], "weight": m["weight"]} for m in (gap["missing"] if gap else [])]

    rows = []
    for g in GROUPS:
        row = {"group": g, "current": sum(c["group"] == g for c in current), "acquired": sum(a["group"] == g for a in acquired),
               "missing": sum(m["group"] == g for m in missing)}
        row["current_names"] = [c["name"] for c in current if c["group"] == g]
        row["acquired_names"] = [a["skill"] for a in acquired if a["group"] == g]
        row["missing_names"] = [m["name"] for m in missing if m["group"] == g]
        if row["current"] or row["acquired"] or row["missing"]:
            rows.append(row)

    strongest = None
    scored = {}
    for c in current:
        s = scored.setdefault(c["group"], {"count": 0, "credit": 0.0})
        s["count"] += 1
        s["credit"] += c["credit"]
    if scored:
        g = max(scored, key=lambda k: (scored[k]["credit"], scored[k]["count"]))
        strongest = {"group": g, "count": scored[g]["count"], "avg_credit": round(scored[g]["credit"] / scored[g]["count"], 2)}

    recent = sorted(acquired_all, key=lambda e: e["date"], reverse=True)
    recent = [e for e in recent if start is None or e["date"] >= start][:6]
    prev = None
    if days:
        p0, p1 = start - timedelta(days=days), start - timedelta(days=1)
        prev = sum(p0 <= e["date"] <= p1 for e in events)
    return {"current": current, "missing": missing, "groups": rows, "acquired_count": len(acquired), "acquired_prev": prev,
            "acquired_total": len(acquired_all), "recent": recent, "strongest": strongest,
            "top_win": (max(acquired, key=lambda e: (e["hours"], e["date"])) if acquired else None)}


# ------------------------------------------------------------------------------------------ roadmap
def roadmap_analytics(raw: dict) -> dict:
    plan, prog, events = raw["plan"], raw["progress"], raw["events"]
    if not plan:
        return {"has_roadmap": False}
    done_names = {e["skill"] for e in events}
    stage_rows = []
    for st, ps in zip(plan["stages"], prog["stages"]):
        stage_rows.append({"index": st["index"], "name": st["name"], "status": ps["status"], "done": ps["done"],
                           "total": ps["total"], "pct": ps["pct"], "hours": st["hours"]})
    upcoming = [{"name": s["name"], "stage": st["name"], "hours": s["hours"], "priority": s["priority"]}
                for st in plan["stages"] for s in st["skills"] if s["name"] not in done_names]
    status = Counter(r["status"] for r in stage_rows)
    return {"has_roadmap": True, "career": plan["career"], "level": plan["level"], "pct": prog["pct"], "done": prog["done"],
            "total": prog["total"], "hours_done": prog["hours_done"], "hours_left": prog["hours_left"],
            "plan_hours": plan["total_hours"], "finish_on": plan.get("finish_on"), "stages": stage_rows,
            "stages_completed": status["done"] + status["covered"], "stages_in_progress": status["doing"],
            "stages_remaining": status["todo"], "stage_count": len(stage_rows),
            "upcoming": upcoming, "next": prog["next"], "recent_done": sorted(events, key=lambda e: e["date"], reverse=True)[:5]}


# ------------------------------------------------------------------------------------------ jobs
def _in_window(day: Optional[date], start: Optional[date], today: date) -> bool:
    return day is not None and (start is None or start <= day <= today)


def jobs_analytics(raw: dict, days: Optional[int]) -> dict:
    results, cand = raw["results"], raw["cand"]
    today = raw["today"]
    start = today - timedelta(days=days - 1) if days else None
    scores = [r["score"] for r in results]
    bands = [{"label": name, "count": sum(lo <= s < hi for s in scores)} for name, lo, hi in SCORE_BANDS]
    top = results[:TOP_JOBS_FOR_SKILLS]
    counter = Counter(s for r in top for s in r["job"]["required"])
    requested = [{"skill": s, "jobs": n, "have": s in cand["skills"], "group": group_of_skill(s)}
                 for s, n in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:8]]
    history = [s for s in raw["snapshots"] if s["avg_match"] is not None
               and (start is None or date.fromisoformat(s["snap_date"]) >= start)]
    return {"total": len(results), "best": results[0] if results else None, "avg": _avg(scores), "top5_avg": _avg(scores[:5]),
            "strong": sum(s >= job_matching.UNLOCK_AT for s in scores), "strong_at": job_matching.UNLOCK_AT, "bands": bands,
            "top": [{"title": r["job"]["title"], "company": r["job"]["company"], "score": r["score"], "label": r["label"]}
                    for r in results[:8]], "requested": requested, "requested_from": len(top),
            "history": history, "no_skills": not cand["skills"]}


# ------------------------------------------------------------------------------------------ CV
def cv_analytics(raw: dict, days: Optional[int]) -> dict:
    analyses, latest = raw["analyses"], raw["cv_latest"]
    if not analyses:
        return {"has_cv": False}
    today = raw["today"]
    start = today - timedelta(days=days - 1) if days else None
    oldest_first = list(reversed(analyses))
    history = [{"id": a["id"], "file": a["file_name"], "role": a["target_role"], "score": a["score"], "date": a["date"]}
               for a in oldest_first if start is None or _in_window(a["date"], start, today)]
    first, prev = oldest_first[0], (oldest_first[-2] if len(oldest_first) > 1 else None)
    ratios = {k: v["points"] / v["max"] for k, v in latest["breakdown"].items() if v.get("max")}
    weakest = min(ratios, key=ratios.get) if ratios else None
    return {"has_cv": True, "latest": latest, "count": len(analyses), "history": history,
            "improvement": latest["score"] - first["score"] if len(analyses) > 1 else None,
            "since_last": latest["score"] - prev["score"] if prev else None,
            "weakest": ({"name": weakest, "pct": round(100 * ratios[weakest])} if weakest else None),
            "strongest": ({"name": max(ratios, key=ratios.get), "pct": round(100 * max(ratios.values()))} if ratios else None)}


# ------------------------------------------------------------------------------------------ career + cards
def career_analytics(raw: dict, days: Optional[int], roadmap: dict) -> dict:
    gap = raw["gap"]
    today = raw["today"]
    start = today - timedelta(days=days - 1) if days else None
    history = [s for s in raw["snapshots"] if s["readiness"] is not None
               and (start is None or date.fromisoformat(s["snap_date"]) >= start)]
    baseline = next((s for s in history if s["snap_date"] < today.isoformat()), None)
    now = gap["match_pct"] if gap else None
    return {"has_career": gap is not None, "career": raw["career"], "readiness": now,
            "have": gap["have"] if gap else None, "need": gap["need"] if gap else None, "total": gap["total"] if gap else None,
            "missing_count": gap["missing_count"] if gap else None, "partial_count": gap["partial_count"] if gap else None,
            "stages": ([{"name": s["name"], "pct": s["progress_pct"], "left": len(s["items"])} for s in gap["stages"]] if gap else []),
            "total_weeks": gap["total_weeks"] if gap else None, "total_duration": gap["total_duration"] if gap else None,
            "coverage": gap["category_coverage"] if gap else {}, "history": history,
            "delta": _delta(now, baseline["readiness"]) if baseline else None,
            "baseline_date": baseline["snap_date"] if baseline else None,
            "roadmap_pct": roadmap.get("pct") if roadmap.get("has_roadmap") else None}


def summary_cards(career: dict, skills: dict, learning: dict, jobs: dict, roadmap: dict, days: Optional[int], label: str, raw: dict) -> list:
    snaps = [s for s in jobs["history"] if s["snap_date"] < raw["today"].isoformat() and s["top5_avg"] is not None]
    job_delta = _delta(jobs["top5_avg"], snaps[0]["top5_avg"]) if snaps else None
    period = label.lower() if days else "all time"
    plan_total = roadmap["total"] if roadmap.get("has_roadmap") else None
    return [
        {"key": "career", "label": "Career Progress", "icon": "target", "tone": "blue", "value": career["readiness"], "unit": "%",
         "progress": career["readiness"], "delta": career["delta"], "delta_unit": " pts",
         "delta_note": (f"since {career['baseline_date']}" if career["baseline_date"] else ""),
         "sub": (f"Readiness for {career['career']}" if career["has_career"] else ""),
         "empty": "Choose a target career in Skill Gap Analysis"},
        {"key": "skills", "label": "Skills Acquired", "icon": "cap", "tone": "mint",
         "value": skills["acquired_count"] if roadmap.get("has_roadmap") else None, "unit": "",
         "progress": _pct(skills["acquired_total"], plan_total) if plan_total else None,
         "delta": (skills["acquired_count"] - skills["acquired_prev"]) if skills["acquired_prev"] is not None and roadmap.get("has_roadmap") else None,
         "delta_unit": "", "delta_note": f"vs previous {days} days" if days else "", "sub": (f"{skills['acquired_total']} of {plan_total} roadmap skills · {period}" if plan_total else ""),
         "empty": "Generate a Learning Roadmap to track new skills"},
        {"key": "hours", "label": "Learning Hours", "icon": "book", "tone": "cream",
         "value": learning["window_hours"] if learning["has_data"] else None, "unit": " h",
         "progress": _pct(roadmap["hours_done"], roadmap["plan_hours"]) if roadmap.get("has_roadmap") and roadmap["plan_hours"] else None,
         "delta": _delta(learning["window_hours"], learning["prev_hours"]) if learning["has_data"] else None, "delta_unit": " h",
         "delta_note": f"vs previous {days} days" if days else "",
         "sub": (f"Estimated study time · {period}" if learning["has_data"] else ""),
         "empty": "Tick skills in your roadmap to log learning"},
        {"key": "match", "label": "Job Match Score", "icon": "star", "tone": "lav", "value": jobs["top5_avg"], "unit": "%",
         "progress": jobs["top5_avg"], "delta": job_delta, "delta_unit": " pts",
         "delta_note": (f"since {snaps[0]['snap_date']}" if snaps else ""),
         "sub": (f"Average of your 5 best matches · best {jobs['best']['score']}%" if jobs["best"] else ""),
         "empty": "No jobs available to score"},
    ]


# ------------------------------------------------------------------------------------------ insights
def insights(raw: dict, career: dict, skills: dict, learning: dict, roadmap: dict, jobs: dict, cv: dict) -> list:
    out = []

    def add(icon: str, tone: str, title: str, text: str) -> None:
        out.append({"icon": icon, "tone": tone, "title": title, "text": text})

    s = skills["strongest"]
    if s:
        add("layers", "blue", "Strongest skill category",
            f"{s['group']}: {s['count']} skill{'s' if s['count'] != 1 else ''} at an average proficiency of {round(s['avg_credit'] * 100)}%.")
    win = skills["top_win"]
    if win:
        add("trophy", "mint", "Biggest learning win",
            f"{win['skill']} ({win['stage']}) took about {win['hours']} h of planned study and was completed on {win['date']:%d %b}.")
    if learning["has_data"]:
        diff = _hours(learning["week_hours"] - learning["last_week_hours"])
        trend = (f"{abs(diff):g} h more than the 7 days before" if diff > 0 else f"{abs(diff):g} h less than the 7 days before"
                 if diff < 0 else "the same as the 7 days before")
        add("chart", "cream", "Your learning activity this week",
            f"About {learning['week_hours']:g} h in the last 7 days, {trend}. Current streak: {learning['streak']} day(s).")
    else:
        add("chart", "cream", "Your learning activity this week",
            "No completed roadmap skills yet. Tick a skill in the Learning Roadmap and your study time will appear here.")
    gap = raw["gap"]
    if gap:
        high = [m for m in gap["missing"] if m["weight"] == 3][:3]
        if high:
            add("target", "lav", "Remaining high-priority skills",
                f"{', '.join(m['name'] for m in high)}"
                f"{' and more' if sum(m['weight'] == 3 for m in gap['missing']) > 3 else ''} "
                f"{'are' if len(high) > 1 else 'is'} rated High importance for {raw['career']}.")
        else:
            add("target", "lav", "Remaining high-priority skills", f"You cover every High-importance skill for {raw['career']}.")
        nxt = gap["recommendations"][0] if gap["recommendations"] else None
        add("bulb", "blue", "Your current career readiness",
            f"{gap['match_pct']}% ready for {raw['career']} ({gap['have']} of {gap['total']} requirements met)."
            + (f" Next step: {nxt['title']}." if nxt and nxt["skill"] else ""))
    else:
        add("bulb", "blue", "Your current career readiness",
            "Choose a target career in Skill Gap Analysis to see how ready you are and which skills to learn.")
    top_rec = (raw["recs"]["skills"] or [None])[0]
    if top_rec:
        add("star", "mint", "Best skill to learn for jobs",
            f"{top_rec['skill']} would raise your match on {top_rec['jobs']} job(s) by about {top_rec['avg_gain']} points each"
            + (f" and make {top_rec['unlocked']} of them a strong match." if top_rec["unlocked"] else "."))
    if cv.get("has_cv") and cv["weakest"]:
        w = cv["weakest"]
        add("book", "cream", "CV improvement area",
            f"Your CV scores lowest on {w['name'].lower()} ({w['pct']}% of its points). Improving it is the fastest way to raise your {cv['latest']['score']}/100 score.")
    return out


# ------------------------------------------------------------------------------------------ main entry
def build_dashboard(raw: dict, window: str = DEFAULT_WINDOW) -> dict:
    if window not in WINDOWS:
        raise ValueError(f"Unknown window: {window}")
    days = WINDOWS[window]
    learning = learning_activity(raw, days)
    skills = skills_analytics(raw, days)
    roadmap = roadmap_analytics(raw)
    career = career_analytics(raw, days, roadmap)
    jobs = jobs_analytics(raw, days)
    cv = cv_analytics(raw, days)
    return {"window": window, "days": days, "today": raw["today"], "first_name": raw["first_name"],
            "cards": summary_cards(career, skills, learning, jobs, roadmap, days, window, raw), "career": career,
            "skills": skills, "learning": learning, "roadmap": roadmap, "jobs": jobs, "cv": cv,
            "insights": insights(raw, career, skills, learning, roadmap, jobs, cv)}
