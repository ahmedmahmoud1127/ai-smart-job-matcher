"""Education, Skills, Experience, Projects and Languages (all built on crud_section)."""
from datetime import date
from html import escape as esc

from components.profile.validation import normalize_url, valid_url
from components.profile.widgets import LEVEL_ORDER, crud_section

SKILL_LEVELS = LEVEL_ORDER[:4]
LANG_LEVELS = ["Beginner", "Intermediate", "Advanced", "Native"]
SKILL_CATEGORIES = ["Programming Language", "Web Development", "Database", "Data & AI", "Framework",
                    "Tools & DevOps", "Other"]


def _level_dots(level: str, levels: list) -> str:
    n = levels.index(level) + 1 if level in levels else 0
    return '<span class="dots">' + "".join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(len(levels))) + "</span>"


def _month(s: str) -> str:
    try:
        return date.fromisoformat(s).strftime("%b %Y")
    except (TypeError, ValueError):
        return ""


# ---------------------------------------------------------------- Education
def _education_html(r: dict) -> str:
    meta = " · ".join(esc(str(x)) for x in (r["academic_year"], f"Class of {r['graduation_year']}" if r["graduation_year"] else "") if x)
    gpa = f'<span class="chip">GPA {r["gpa"]:.2f}</span>' if r["gpa"] is not None else ""
    return (f'<div class="item-title">{esc(r["university"])}</div>'
            f'<div class="item-meta">{esc(r["degree"])} · {esc(r["major"])} — {esc(r["faculty"])}</div>'
            f'<div class="item-meta">{meta} {gpa}</div>')


def _validate_education(d: dict, _cur) -> list:
    errs = []
    g = d["gpa"]
    if g == "":
        d["gpa"] = None
    else:
        try:
            d["gpa"] = float(g)
            if not 0 <= d["gpa"] <= 4:
                errs.append("GPA must be between 0 and 4.0.")
        except ValueError:
            errs.append("GPA must be a number (e.g. 3.5).")
    return errs


def render_education() -> None:
    crud_section(
        table="education", prefix="edu", title="Education", icon_name="cap", noun="education",
        subtitle="Your university, major and graduation details.", add_label="Add education",
        empty_text="No education added yet. Add your university to improve your matches.",
        fields=[
            dict(name="university", label="University Name", required=True),
            dict(name="faculty", label="Faculty / College", required=True),
            dict(name="major", label="Major / Department", required=True),
            dict(name="degree", label="Degree", kind="select", options=["Bachelor's", "Diploma", "Master's", "PhD", "Other"]),
            dict(name="academic_year", label="Academic Year", kind="select",
                 options=["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year", "Graduated"]),
            dict(name="graduation_year", label="Graduation Year", kind="year"),
            dict(name="gpa", label="Current GPA (optional)", kind="float_opt", placeholder="e.g. 3.5 (scale 0 – 4)"),
        ], render_item=_education_html, validate=_validate_education)


# ------------------------------------------------------------------- Skills
def _skill_html(r: dict) -> str:
    return (f'<div class="item-title">{esc(r["name"])}</div><div class="item-meta">{esc(r["category"])}</div>'
            f'<div class="lvl lvl-{r["level"].lower()}">{_level_dots(r["level"], SKILL_LEVELS)}</div>')


def render_skills() -> None:
    crud_section(
        table="skills", prefix="skill", title="Technical Skills", icon_name="layers", noun="skill",
        subtitle="Add the skills you have and how well you know them.", add_label="Add skill",
        empty_text="No skills yet. Add Python, SQL, Django or anything you work with.",
        fields=[
            dict(name="name", label="Skill Name", required=True, placeholder="e.g. Django"),
            dict(name="category", label="Skill Category", kind="select", options=SKILL_CATEGORIES),
            dict(name="level", label="Proficiency Level", kind="select", options=SKILL_LEVELS),
        ], render_item=_skill_html, grid_cols=3, quick=("level", SKILL_LEVELS))


# --------------------------------------------------------------- Experience
def _experience_html(r: dict) -> str:
    end = _month(r["end_date"]) or "Present"
    desc = f'<div class="item-desc">{esc(r["description"])}</div>' if r["description"] else ""
    return (f'<div class="item-title">{esc(r["job_title"])} <span class="chip">{esc(r["employment_type"])}</span></div>'
            f'<div class="item-meta">{esc(r["company"])} · {_month(r["start_date"])} – {end}</div>{desc}')


def _validate_experience(d: dict, _cur) -> list:
    if d["end_date"] and d["end_date"] < d["start_date"]:
        return ["End date cannot be before the start date."]
    return []


def render_experience() -> None:
    crud_section(
        table="work_experience", prefix="exp", title="Work Experience", icon_name="briefcase", noun="experience",
        subtitle="Jobs, internships and volunteering.", add_label="Add experience",
        empty_text="No experience yet. Internships and volunteering count too.",
        fields=[
            dict(name="job_title", label="Job Title", required=True),
            dict(name="company", label="Company Name", required=True),
            dict(name="employment_type", label="Employment Type", kind="select",
                 options=["Full-time", "Part-time", "Internship", "Freelance", "Volunteering"]),
            dict(name="start_date", label="Start Date", kind="date"),
            dict(name="end_date", label="End Date", kind="date_opt", ongoing_label="I currently work here"),
            dict(name="description", label="Description", kind="textarea", full=True,
                 placeholder="What did you build or achieve?"),
        ], render_item=_experience_html, validate=_validate_experience)


# ----------------------------------------------------------------- Projects
def _project_html(r: dict) -> str:
    techs = "".join(f'<span class="chip">{esc(t.strip())}</span>' for t in r["technologies"].split(",") if t.strip())
    links = f'<a href="{esc(r["github_url"])}" target="_blank" rel="noopener">GitHub ↗</a>'
    if r["demo_url"]:
        links += f' <a href="{esc(r["demo_url"])}" target="_blank" rel="noopener">Live demo ↗</a>'
    return (f'<div class="item-title">{esc(r["name"])}</div><div class="item-desc">{esc(r["description"])}</div>'
            f'<div class="chips">{techs}</div><div class="links">{links}</div>')


def _validate_project(d: dict, _cur) -> list:
    errs = []
    d["github_url"], d["demo_url"] = normalize_url(d["github_url"]), normalize_url(d["demo_url"])
    if not valid_url(d["github_url"]):
        errs.append("GitHub Repository Link must be a valid URL.")
    if d["demo_url"] and not valid_url(d["demo_url"]):
        errs.append("Live Demo Link must be a valid URL.")
    return errs


def render_projects() -> None:
    crud_section(
        table="projects", prefix="proj", title="Projects", icon_name="target", noun="project",
        subtitle="Show what you have built.", add_label="Add project",
        empty_text="No projects yet. Add one with a GitHub link to stand out.",
        fields=[
            dict(name="name", label="Project Name", required=True),
            dict(name="technologies", label="Technologies Used", required=True, placeholder="Python, Django, SQL"),
            dict(name="github_url", label="GitHub Repository Link", required=True, placeholder="https://github.com/you/repo"),
            dict(name="demo_url", label="Live Demo Link (optional)"),
            dict(name="description", label="Project Description", kind="textarea", full=True, required=True),
        ], render_item=_project_html, validate=_validate_project, grid_cols=2)


# ---------------------------------------------------------------- Languages
def _language_html(r: dict) -> str:
    return (f'<div class="item-title">{esc(r["name"])}</div>'
            f'<div class="lvl lvl-{r["level"].lower()}">{_level_dots(r["level"], LANG_LEVELS)}</div>')


def render_languages() -> None:
    crud_section(
        table="languages", prefix="lang", title="Languages", icon_name="book", noun="language",
        subtitle="Languages you can work in.", add_label="Add language",
        empty_text="No languages yet. Add Arabic, English or others.",
        fields=[
            dict(name="name", label="Language", required=True, placeholder="e.g. German"),
            dict(name="level", label="Proficiency Level", kind="select", options=LANG_LEVELS),
        ], render_item=_language_html, quick=("level", LANG_LEVELS))
