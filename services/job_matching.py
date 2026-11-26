"""Smart Job Matching engine: pure Python, deterministic, no external AI APIs.

The candidate (skills, education, experience, preferences) is built from My Profile and the latest
CV Analyzer result. Each job gets a 0-100 score made of five weighted components:

    required skills 40 | preferred skills 15 | education 15 | experience 15 | career preferences 15

A component that cannot be evaluated (e.g. the user has not set career preferences, or the job lists no
preferred skills) is left out and the remaining weights are rescaled to 100, so a missing profile section
never silently drags the score down or up.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from data.jobs_catalog import JOBS
from data.skills_catalog import SKILL_CATEGORY
from database import cv_repository as cv_repo
from database.session import resolve_user_id
from services import profile_data
from services.skills_extractor import canonical_names, find_skills

WEIGHTS = {"required": 40, "preferred": 15, "education": 15, "experience": 15, "career": 15}
LABELS = {"required": "Required skills", "preferred": "Preferred skills", "education": "Education",
          "experience": "Experience", "career": "Career preferences"}

LEVEL_CREDIT = {"Beginner": 0.5, "Intermediate": 0.8, "Advanced": 1.0, "Expert": 1.0}  # profile proficiency
CV_CREDIT, PROJECT_CREDIT, EXPERIENCE_CREDIT = 0.75, 0.7, 0.8  # skills found elsewhere count slightly less
RELATED_FACTOR = 0.5   # a closely related skill earns half credit (e.g. MySQL for a SQL requirement)
LEARN_CREDIT = 0.8     # what-if: the user learns a skill up to roughly Intermediate level
UNLOCK_AT = 70         # a job counts as a "strong match" from this score
REALISTIC_AT = 35      # skill advice only considers jobs scoring at least this much...
TARGET_JOBS = 12       # ...and only the user's closest-fitting jobs (top N by score)

# job skill -> skills the user may already have that give partial credit
RELATED = {
    "SQL": ["MySQL", "PostgreSQL", "SQLite", "Oracle"], "MySQL": ["SQL", "PostgreSQL"], "PostgreSQL": ["SQL", "MySQL"],
    "SQLite": ["SQL", "MySQL"], "Database Management": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite"],
    "Git": ["GitHub"], "GitHub": ["Git"],
    "REST APIs": ["Django", "Flask", "FastAPI", "Express.js", "Node.js", "Spring Boot", "Laravel"],
    "Data Visualization": ["Matplotlib", "Plotly", "Power BI", "Tableau"],
    "Data Analysis": ["Pandas", "Statistics"], "Deep Learning": ["TensorFlow", "PyTorch", "Keras"],
    "Machine Learning": ["Scikit-learn", "Deep Learning"], "Scikit-learn": ["Machine Learning"],
    "TensorFlow": ["Keras", "PyTorch"], "PyTorch": ["TensorFlow", "Keras"], "Keras": ["TensorFlow"],
    "Networking": ["Network Security"], "Network Security": ["Networking", "Cybersecurity"],
    "Cybersecurity": ["Network Security", "Penetration Testing"], "Microservices": ["Docker", "Kubernetes"],
    "Unit Testing": ["Postman"], "CI/CD": ["Docker", "GitHub"], "Agile": ["Scrum", "Jira"], "Scrum": ["Agile"],
    "Django": ["Flask", "FastAPI"], "Flask": ["Django", "FastAPI"], "FastAPI": ["Flask", "Django"],
    "React": ["Vue.js", "Angular"], "Vue.js": ["React", "Angular"], "Angular": ["React", "Vue.js"],
    "Express.js": ["Node.js"], "Node.js": ["Express.js"], "TypeScript": ["JavaScript"],
    "Tailwind CSS": ["Bootstrap", "CSS"], "Bootstrap": ["CSS"], "Kubernetes": ["Docker"],
    "AWS": ["Azure", "Google Cloud"], "Azure": ["AWS", "Google Cloud"], "Google Cloud": ["AWS", "Azure"],
    "Power BI": ["Tableau"], "Tableau": ["Power BI"], "Statistics": ["Data Analysis"],
}

DEGREE_RANK = {"Diploma": 1, "Bachelor's": 2, "Master's": 3, "PhD": 4}
ROLE_SIBLINGS = {  # target role -> roles that are close enough for half credit
    "Backend Developer": {"Full Stack Developer", "Software Engineer"},
    "Frontend Developer": {"Full Stack Developer"},
    "Full Stack Developer": {"Backend Developer", "Frontend Developer", "Software Engineer"},
    "Software Engineer": {"Backend Developer", "Full Stack Developer"},
    "Data Analyst": {"Machine Learning Engineer"}, "Machine Learning Engineer": {"Data Analyst"},
}
EMP_FACTOR = {"Full-time": 1.0, "Part-time": 0.5, "Internship": 0.6, "Freelance": 0.7, "Volunteering": 0.4}
STRONG_FIELDS = ("comput", "software", "informat", "data", "artificial", "cyber", "program", "intellig")
ADJACENT_FIELDS = ("engineer", "science", "math", "statist", "physic", "technolog", "electr", "communic")

LEARN_HINTS = {
    "Django": "Follow the official Django tutorial, then build a small blog or to-do app with a database.",
    "Flask": "Build a small REST API with Flask and connect it to SQLite.",
    "FastAPI": "Build a CRUD API with FastAPI and explore its automatic documentation.",
    "REST APIs": "Learn HTTP methods and status codes, then build and test an API with Postman.",
    "Docker": "Containerise one of your projects with a Dockerfile and run it with docker compose.",
    "Kubernetes": "Learn Docker first, then deploy a small app to a local cluster with minikube.",
    "Unit Testing": "Write pytest tests for an existing project and aim for meaningful coverage.",
    "Git": "Practise branches, pull requests and merge conflicts on a GitHub repository.",
    "GitHub": "Publish your projects on GitHub with clear README files.",
    "React": "Complete the official React tutorial, then rebuild one of your pages as components.",
    "TypeScript": "Convert a small JavaScript project to TypeScript to learn types step by step.",
    "Node.js": "Build a small Express server with a few routes and a database.",
    "PostgreSQL": "Install PostgreSQL locally and move one of your SQLite projects to it.",
    "MySQL": "Practise joins and indexes on a sample database such as Sakila.",
    "MongoDB": "Build a small app that stores documents in MongoDB Atlas (free tier).",
    "SQL": "Practise joins, grouping and subqueries on a public dataset.",
    "Linux": "Use a Linux terminal daily: files, permissions, processes and shell scripts.",
    "AWS": "Follow the AWS Cloud Practitioner path and deploy one app on the free tier.",
    "CI/CD": "Add a GitHub Actions workflow that runs your tests on every push.",
    "Pandas": "Clean and analyse a Kaggle dataset using only pandas.",
    "NumPy": "Work through NumPy array exercises: indexing, broadcasting and vectorised maths.",
    "Statistics": "Cover descriptive statistics, distributions and hypothesis testing with Python examples.",
    "Scikit-learn": "Train classification and regression models on Kaggle datasets and compare metrics.",
    "Deep Learning": "Take an introductory deep-learning course and train a small neural network.",
    "TensorFlow": "Build an image classifier with TensorFlow/Keras on a public dataset.",
    "PyTorch": "Follow the PyTorch beginner tutorials and train a small model.",
    "NLP": "Build a text classifier, then try transformer models from Hugging Face.",
    "Computer Vision": "Practise image classification and detection with OpenCV and a pretrained model.",
    "Power BI": "Build a three-page dashboard from a public dataset and publish it.",
    "Tableau": "Recreate a Tableau Public dashboard using your own data.",
    "Microsoft Excel": "Learn pivot tables, lookups and charts by analysing a sample dataset.",
    "Data Visualization": "Make clear charts with Matplotlib or Plotly and write one insight per chart.",
    "Data Analysis": "Complete an end-to-end analysis project: question, cleaning, charts, conclusions.",
    "Data Cleaning": "Practise handling missing values, duplicates and wrong types on messy data.",
    "Matplotlib": "Reproduce common chart types and customise labels, colours and layouts.",
    "HTML": "Build a multi-page static site with semantic HTML.",
    "CSS": "Recreate a few real web pages using Flexbox and Grid.",
    "JavaScript": "Build small interactive projects (to-do list, quiz) without a framework.",
    "Vue.js": "Follow the Vue tutorial and build a small single-page app.",
    "Angular": "Follow the Angular tour of heroes tutorial.",
    "Tailwind CSS": "Restyle one of your pages using Tailwind utility classes.",
    "Bootstrap": "Make a responsive landing page with the Bootstrap grid.",
    "Figma": "Design a simple app screen flow and hand it off as a prototype.",
    "Java": "Practise object-oriented programming and collections with small console projects.",
    "Spring Boot": "Build a REST API with Spring Boot and a relational database.",
    "C++": "Practise pointers, classes and the STL with algorithm problems.",
    "Kotlin": "Build a small Android app with Kotlin and Jetpack Compose.",
    "Dart": "Build a small Flutter app that calls a public API.",
    "Firebase": "Add Firebase authentication and a database to a small app.",
    "PHP": "Build a small CRUD application in plain PHP with MySQL.",
    "Laravel": "Follow the Laravel Bootcamp and build a small application.",
    "Microservices": "Split a small app into two services that communicate over HTTP.",
    "Agile": "Learn Scrum basics and run your own projects in short sprints on a board.",
    "Cybersecurity": "Start with security fundamentals and practise on TryHackMe beginner rooms.",
    "Networking": "Learn the TCP/IP model, DNS and HTTP, then explore traffic with Wireshark.",
    "Network Security": "Study firewalls, VPNs and common network attacks with hands-on labs.",
    "Penetration Testing": "Practise legal labs on Hack The Box or TryHackMe and write short reports.",
    "OWASP": "Work through the OWASP Top 10 using the deliberately vulnerable Juice Shop app.",
    "SIEM": "Set up a free SIEM such as Wazuh or Splunk Free and practise reading alerts.",
    "Wireshark": "Capture and analyse your own network traffic to understand common protocols.",
    "Redis": "Add Redis caching to one of your APIs and measure the speed-up.",
    "Postman": "Create a Postman collection with automated tests for an API.",
    "Jira": "Manage a personal project with a Jira or Trello board.",
    "Database Management": "Learn normalisation, indexes and transactions by designing a schema.",
    "Machine Learning": "Complete an introductory ML course and finish two end-to-end projects.",
}
CATEGORY_HINTS = {
    "Programming Languages": "Solve small exercises, then build one project that uses it.",
    "Web Development": "Follow the official tutorial, then build a small project with it.",
    "Data Science": "Practise on a public Kaggle dataset and publish the notebook.",
    "Databases": "Design a small schema and practise queries on sample data.",
    "Tools & Technologies": "Use it in one of your own projects and document what you did.",
    "Soft Skills": "Practise it in team projects and mention concrete examples in your CV.",
}


def learn_hint(skill: str) -> str:
    return LEARN_HINTS.get(skill) or CATEGORY_HINTS.get(SKILL_CATEGORY.get(skill, ""), f"Take a beginner course in {skill} and use it in a small project.")


# ---------------------------------------------------------------------------------------- candidate
def degree_rank(text: str) -> int:
    t = (text or "").lower()
    if re.search(r"ph\.?d|doctor", t):
        return 4
    if re.search(r"master|m\.?\s?sc|mba", t):
        return 3
    if re.search(r"bachelor|b\.?\s?sc|b\.?\s?eng|b\.?\s?tech", t):
        return 2
    return 1  # diploma / other


def _years(row: dict, today: date) -> float:
    try:
        start = date.fromisoformat(row.get("start_date") or "")
        end = date.fromisoformat(row["end_date"]) if row.get("end_date") else today
    except ValueError:
        return 0.0
    end = min(end, today)
    return max(0.0, (end - start).days / 365.25) * EMP_FACTOR.get(row.get("employment_type"), 1.0)


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def build_candidate(user_id: int | None = None, today: Optional[date] = None) -> dict:
    """Collect everything we know about the user from My Profile and the latest CV Analyzer result."""
    user_id = resolve_user_id(user_id)
    today = today or date.today()
    prof = profile_data.get_full_profile(user_id)
    analyses = cv_repo.list_analyses(user_id)
    cv = cv_repo.get_analysis(analyses[0]["id"], user_id) if analyses else None

    skills: dict = {}

    def add(name: str, credit: float, source: str) -> None:
        cur = skills.setdefault(name, {"credit": 0.0, "sources": []})
        cur["credit"] = max(cur["credit"], credit)
        if source not in cur["sources"]:
            cur["sources"].append(source)

    for row in prof["skills"]:
        for name in canonical_names(row["name"]) or {row["name"]}:
            add(name, LEVEL_CREDIT.get(row["level"], 0.7), "My Profile")
    for p in prof["projects"]:
        for s in find_skills(f"{p['name']} {p['technologies']} {p['description']}"):
            add(s["name"], PROJECT_CREDIT, "Projects")
    for e in prof["experience"]:
        for s in find_skills(f"{e['job_title']} {e['description']}"):
            add(s["name"], EXPERIENCE_CREDIT, "Experience")
    if cv:
        for name in cv["skills"]:
            add(name, CV_CREDIT, "CV Analyzer")

    # education: highest degree wins; fall back to what the CV analysis found
    edu_rows = [{"degree": e["degree"], "major": e["major"], "faculty": e["faculty"], "university": e["university"],
                 "in_progress": (e["academic_year"] or "Graduated") != "Graduated", "source": "My Profile"}
                for e in prof["education"]]
    if not edu_rows and cv:
        edu_rows = [{"degree": e.get("degree", ""), "major": e.get("major", ""), "faculty": e.get("faculty", ""),
                     "university": e.get("university", ""), "in_progress": False, "source": "CV Analyzer"}
                    for e in cv["result"].get("education", [])]
    for e in edu_rows:
        e["rank"] = degree_rank(e["degree"])
    education = max(edu_rows, key=lambda e: e["rank"]) if edu_rows else None

    # experience: dated work history + a small credit for projects and CV-only positions
    work_years = sum(_years(e, today) for e in prof["experience"])
    profile_titles = {_norm(e["job_title"]) for e in prof["experience"]}
    cv_new = [e for e in (cv["result"].get("experience", []) if cv else []) if _norm(e.get("title", "")) not in profile_titles]
    project_bonus = min(0.6, 0.15 * len(prof["projects"]))
    cv_bonus = min(1.0, 0.4 * len(cv_new))
    experience = {"years": round(work_years + project_bonus + cv_bonus, 2), "work_years": round(work_years, 2),
                  "positions": len(prof["experience"]), "cv_positions": len(cv_new), "projects": len(prof["projects"])}

    return {"skills": skills, "education": education, "experience": experience, "preferences": prof["preferences"],
            "profile_skill_count": len(prof["skills"]), "full_name": prof["user"].get("full_name", ""),
            "cv": ({"id": cv["id"], "file_name": cv["file_name"], "created_at": cv["created_at"], "skill_count": len(cv["skills"])}
                   if cv else None)}


# ---------------------------------------------------------------------------------------- scoring
def _credit(skill: str, skills: dict) -> tuple:
    """(credit 0-1, kind 'direct' | 'related' | 'missing', related skill used)."""
    direct = skills.get(skill)
    if direct and direct["credit"] > 0:
        return direct["credit"], "direct", None
    best, via = 0.0, None
    for rel in RELATED.get(skill, ()):
        c = skills.get(rel, {}).get("credit", 0.0) * RELATED_FACTOR
        if c > best:
            best, via = c, rel
    return (best, "related", via) if best else (0.0, "missing", None)


def _skill_part(names: list, skills: dict) -> dict:
    matched, related, missing, total = [], [], [], 0.0
    for n in names:
        c, kind, via = _credit(n, skills)
        total += c
        (matched if kind == "direct" else related if kind == "related" else missing).append(
            n if kind != "related" else {"skill": n, "via": via})
    return {"score": total / len(names) if names else None, "matched": matched, "related": related, "missing": missing}


def _field_relevance(edu: dict) -> float:
    text = f"{edu.get('major', '')} {edu.get('faculty', '')}".lower()
    if any(k in text for k in STRONG_FIELDS):
        return 1.0
    return 0.6 if any(k in text for k in ADJACENT_FIELDS) else 0.2


def _education_part(job: dict, edu: Optional[dict]) -> tuple:
    if not edu:
        return 0.0, "No education found. Add it in My Profile or analyze your CV."
    need = DEGREE_RANK.get(job["education"], 1)
    degree = min(1.0, edu["rank"] / need)
    note = ""
    if edu["in_progress"] and job["level"] != "Internship":
        degree *= 0.9
        note = " (still studying, counted at 90%)"
    field = _field_relevance(edu)
    field_txt = "highly relevant field" if field == 1 else "related field" if field >= 0.6 else "field not clearly related"
    have = f"{edu['degree'] or 'Degree'}{' in ' + edu['major'] if edu['major'] else ''}"
    return 0.6 * degree + 0.4 * field, f"Needs {job['education']}; you have {have}{note}, {field_txt}."


def _experience_part(job: dict, exp: dict) -> tuple:
    need, have = job["min_years"], exp["years"]
    if need == 0:
        return 1.0, "No prior experience required."
    return min(1.0, have / need), f"Asks for about {need:g} year(s); you have about {have:g} (work, projects and CV positions)."


def _career_part(job: dict, prefs: dict) -> tuple:
    checks = []  # (weight, score, text)
    role = (prefs.get("effective_role") or "").strip()
    if role:
        words = [w for w in role.lower().split() if len(w) > 3]
        if role == job["role"] or role.lower() in job["title"].lower():
            s = 1.0
        elif job["role"] in ROLE_SIBLINGS.get(role, ()):
            s = 0.5
        else:
            s = 0.6 if words and any(w in job["title"].lower() for w in words) else 0.0
        checks.append((0.4, s, f"target role {role}"))
    work = prefs.get("work_type")
    if work:
        s = 1.0 if work == job["work_type"] else 0.5 if "Hybrid" in (work, job["work_type"]) else 0.0
        checks.append((0.2, s, f"{work} work"))
    emp = prefs.get("employment_type")
    if emp:
        checks.append((0.2, 1.0 if emp == job["employment_type"] else 0.0, emp))
    ind = (prefs.get("effective_industry") or "").strip().lower()
    if ind:
        j = job["industry"].lower()
        checks.append((0.2, 1.0 if ind == j or ind in j or j in ind else 0.0, f"{prefs.get('effective_industry')} industry"))
    if not checks:
        return None, "Set your career preferences in My Profile to include them in the score."
    total_w = sum(w for w, _, _ in checks)
    score = sum(w * s for w, s, _ in checks) / total_w
    hit = [t for _, s, t in checks if s >= 1]
    part = [t for _, s, t in checks if 0 < s < 1]
    miss = [t for _, s, t in checks if s == 0]
    bits = ([f"matches {', '.join(hit)}"] if hit else []) + ([f"partly matches {', '.join(part)}"] if part else []) \
        + ([f"differs on {', '.join(miss)}"] if miss else [])
    return score, "Job " + "; ".join(bits) + "."


def label_for(score: float) -> str:
    return ("Excellent match" if score >= 80 else "Strong match" if score >= 65 else "Good match" if score >= 50
            else "Partial match" if score >= 35 else "Low match")


def tier_for(score: float) -> str:
    return "high" if score >= 75 else "mid" if score >= 50 else "low"


def score_job(job: dict, cand: dict) -> dict:
    req = _skill_part(job["required"], cand["skills"])
    pref = _skill_part(job["preferred"], cand["skills"])
    edu_score, edu_note = _education_part(job, cand["education"])
    exp_score, exp_note = _experience_part(job, cand["experience"])
    car_score, car_note = _career_part(job, cand["preferences"])
    notes = {
        "required": f"{len(req['matched'])} of {len(job['required'])} required skills matched"
                    + (f", {len(req['related'])} partly covered by related skills" if req["related"] else "") + ".",
        "preferred": (f"{len(pref['matched'])} of {len(job['preferred'])} preferred skills matched"
                      + (f", {len(pref['related'])} partly covered" if pref["related"] else "") + ".") if job["preferred"] else "",
        "education": edu_note, "experience": exp_note, "career": car_note}
    raw = {"required": req["score"], "preferred": pref["score"], "education": edu_score,
           "experience": exp_score, "career": car_score}
    active = {k: v for k, v in raw.items() if v is not None}
    scale = 100 / sum(WEIGHTS[k] for k in active)
    components, total = [], 0.0
    for k in WEIGHTS:
        used = k in active
        weight = WEIGHTS[k] * scale if used else 0.0
        points = weight * raw[k] if used else 0.0
        total += points
        components.append({"key": k, "label": LABELS[k], "used": used, "weight": round(weight, 1),
                           "pct": round(100 * raw[k]) if used else None, "points": round(points, 1), "note": notes[k]})
    score = int(round(total))
    return {"job": job, "score": score, "raw": total, "label": label_for(score), "tier": tier_for(score),
            "matched_required": req["matched"], "related_required": req["related"], "missing_required": req["missing"],
            "matched_preferred": pref["matched"], "related_preferred": pref["related"], "missing_preferred": pref["missing"],
            "required_pct": round(100 * (req["score"] or 0)), "components": components}


def rank_jobs(cand: dict, jobs: Optional[list] = None) -> list:
    """Score every job and sort best first (ties: more required skills matched, then title)."""
    out = [score_job(j, cand) for j in (JOBS if jobs is None else jobs)]
    return sorted(out, key=lambda r: (-r["score"], -len(r["matched_required"]), r["job"]["title"]))


# ---------------------------------------------------------------------------------------- filters
def filter_jobs(results: list, *, search: str = "", work_type: str = "All", employment: str = "All", level: str = "All",
                city: str = "All", role: str = "All", min_score: int = 0, sort: str = "Best match") -> list:
    tokens = [t for t in re.split(r"\s+", search.lower().strip()) if t]
    out = []
    for r in results:
        j = r["job"]
        if work_type != "All" and j["work_type"] != work_type:
            continue
        if employment != "All" and j["employment_type"] != employment:
            continue
        if level != "All" and j["level"] != level:
            continue
        if city != "All" and j["city"] != city:
            continue
        if role != "All" and j["role"] != role:
            continue
        if r["score"] < min_score:
            continue
        if tokens:
            hay = " ".join([j["title"], j["company"], j["role"], j["industry"], j["city"], j["summary"],
                            j["work_type"], j["employment_type"], j["level"], *j["required"], *j["preferred"]]).lower()
            if not all(t in hay for t in tokens):
                continue
        out.append(r)
    if sort == "Highest salary":
        out.sort(key=lambda r: (-r["job"]["salary_max"], -r["score"]))
    elif sort == "Newest":
        out.sort(key=lambda r: (r["job"]["posted_days"], -r["score"]))
    elif sort == "Title (A-Z)":
        out.sort(key=lambda r: r["job"]["title"])
    return out  # "Best match" keeps the ranking order from rank_jobs


# ---------------------------------------------------------------------------------------- skills to learn
def recommend_skills(cand: dict, results: list, limit: int = 6) -> dict:
    """What-if analysis: for each skill the user lacks, re-score the jobs that ask for it as if the user had
    learned it (to LEARN_CREDIT) and measure the real gain. Returns the ranked skills and a combined projection."""
    targets = [r for r in results[:TARGET_JOBS] if r["score"] >= REALISTIC_AT] or results[:5]  # the jobs the user is closest to
    candidates = {s for r in targets for s in (r["job"]["required"] + r["job"]["preferred"])
                  if cand["skills"].get(s, {}).get("credit", 0) < LEARN_CREDIT
                  and SKILL_CATEGORY.get(s) != "Soft Skills"}

    def with_skills(names) -> dict:
        skills = dict(cand["skills"])
        for n in names:
            skills[n] = {"credit": LEARN_CREDIT, "sources": ["Learning goal"]}
        return {**cand, "skills": skills}

    recs = []
    for skill in candidates:
        hypo = with_skills([skill])
        gains, unlocked = [], 0
        for r in targets:
            j = r["job"]
            if skill not in j["required"] and skill not in j["preferred"]:
                continue
            new = score_job(j, hypo)
            gain = new["raw"] - r["raw"]
            if gain > 0.05:
                gains.append((gain, j))
                unlocked += r["score"] < UNLOCK_AT <= new["score"]
        if not gains:
            continue
        gains.sort(key=lambda g: -g[0])
        needed_required = sum(skill in g[1]["required"] for g in gains)
        recs.append({"skill": skill, "category": SKILL_CATEGORY.get(skill, ""), "jobs": len(gains),
                     "required_in": needed_required, "avg_gain": round(sum(g for g, _ in gains) / len(gains), 1),
                     "total_gain": round(sum(g for g, _ in gains), 1), "unlocked": unlocked,
                     "top_jobs": [j["title"] for _, j in gains[:3]], "hint": learn_hint(skill)})
    recs.sort(key=lambda r: (-r["total_gain"], -r["unlocked"], r["skill"]))
    top = recs[:limit]

    projection = None
    if top:
        picks = [r["skill"] for r in top[:3]]
        after = rank_jobs(with_skills(picks))
        avg = lambda rs: round(sum(x["score"] for x in rs[:5]) / max(1, len(rs[:5])), 1)
        projection = {"skills": picks, "avg_before": avg(results), "avg_after": avg(after),
                      "best_before": results[0]["score"], "best_after": after[0]["score"],
                      "strong_before": sum(r["score"] >= UNLOCK_AT for r in results),
                      "strong_after": sum(r["score"] >= UNLOCK_AT for r in after)}
    return {"skills": top, "projection": projection, "total_candidates": len(recs)}
