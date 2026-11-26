"""Rule-based parsing of CV sections, contact info, education, experience and projects."""
import re

SECTION_ALIASES = {
    "summary": {"summary", "professional summary", "profile", "career objective", "objective", "about me", "about", "personal statement"},
    "education": {"education", "academic background", "academic qualifications", "qualifications", "education & training"},
    "skills": {"skills", "technical skills", "technologies", "core competencies", "skills & tools", "key skills", "tools & technologies", "technical proficiencies"},
    "experience": {"experience", "work experience", "professional experience", "employment", "employment history", "work history",
                   "internships", "internship", "internship experience", "volunteering", "volunteer experience", "practical experience"},
    "projects": {"projects", "academic projects", "personal projects", "selected projects", "key projects"},
    "certifications": {"certifications", "certification", "certificates", "courses", "training", "licenses", "courses & certifications", "licenses & certifications"},
    "languages": {"languages", "language skills"},
}
SECTION_LABELS = {"contact": "Contact Information", "summary": "Professional Summary", "education": "Education",
                  "skills": "Technical Skills", "experience": "Work Experience", "projects": "Projects",
                  "certifications": "Certifications", "languages": "Languages"}
_LOOKUP = {a: k for k, al in SECTION_ALIASES.items() for a in al}

EMAIL_RE = re.compile(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+")
PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\s\-()]{8,16}\d)(?!\d)")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s,;)|]+", re.I)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[^\s,;)|]+", re.I)
BULLET = ("•", "-", "–", "*", "▪", "●", "·", "◦")

TITLE_KW = re.compile(r"\b(developer|engineer|intern|internship|analyst|designer|consultant|manager|administrator|assistant|"
                      r"trainee|specialist|scientist|programmer|volunteer|architect|tester|lead|coordinator|instructor|tutor)\b", re.I)
DEGREE_RE = re.compile(r"\b(Bachelor(?:'s|s)?(?: of [A-Za-z ]+?)?|B\.?\s?Sc\.?|B\.?\s?Eng\.?|B\.?Tech|Master(?:'s|s)?(?: of [A-Za-z ]+?)?|M\.?\s?Sc\.?|MBA|Ph\.?D\.?|Diploma)\b", re.I)
UNI_RE = re.compile(r"((?:University|Institute|Academy|College) of [A-Z][A-Za-z&' ]+?(?=\s*[,|\-–(\n]|\s+\d|$)|[A-Z][A-Za-z&'.]*(?: [A-Z][A-Za-z&'.]*){0,4} (?:University|Institute|Academy|College))")
FACULTY_RE = re.compile(r"(Faculty of [A-Za-z&' ]+?)(?=\s*[,|\-–(\n]|\s+\d|$)", re.I)
MAJORS = ["Computer Science", "Information Technology", "Software Engineering", "Data Science", "Information Systems",
          "Artificial Intelligence", "Cybersecurity", "Computer Engineering", "Electrical Engineering", "Statistics",
          "Mathematics", "Business Administration", "Communications Engineering", "Systems Engineering"]
MAJOR_RE = re.compile("|".join(re.escape(m) for m in MAJORS), re.I)
MEASURE_RE = re.compile(r"\d+\s?%|\b\d{2,}\+?\s+(?:users|customers|requests|records|students|projects|clients)\b|\b(?:increased|reduced|improved|decreased|boosted|saved)\b", re.I)


def split_sections(text: str) -> dict:
    """Split the CV into {section_key: text}. Unlabelled leading text is stored under 'header'."""
    sections, current, buf = {}, "header", []
    for raw in text.split("\n"):
        line = raw.strip()
        key, rest = None, ""
        if line and len(line) <= 45:
            norm = re.sub(r"[^a-z& ]", "", line.lower()).strip()
            if norm in _LOOKUP:
                key = _LOOKUP[norm]
        if key is None and ":" in line:
            head, _, tail = line.partition(":")
            norm = re.sub(r"[^a-z& ]", "", head.lower()).strip()
            if len(head) <= 30 and norm in _LOOKUP and tail.strip():
                key, rest = _LOOKUP[norm], tail.strip()
        if key:
            sections[current] = "\n".join(buf).strip()
            current, buf = key, ([rest] if rest else [])
        else:
            buf.append(raw)
    sections[current] = "\n".join(buf).strip()
    prev = {}
    for k, v in sections.items():  # merge repeated headings
        prev[k] = (prev.get(k, "") + "\n" + v).strip()
    return prev


def extract_contact(text: str) -> dict:
    phone = next((m.group(1).strip() for m in PHONE_RE.finditer(text) if len(re.sub(r"\D", "", m.group(1))) >= 9), "")
    email = EMAIL_RE.search(text)
    li, gh = LINKEDIN_RE.search(text), GITHUB_RE.search(text)
    fix = lambda m: ("" if not m else (m.group(0) if m.group(0).lower().startswith("http") else "https://" + m.group(0)).rstrip(".,"))
    return {"email": email.group(0) if email else "", "phone": phone, "linkedin": fix(li), "github": fix(gh)}


def extract_education(sections: dict, text: str) -> list:
    block = sections.get("education") or text
    uni = UNI_RE.search(block)
    fac = FACULTY_RE.search(block)
    deg = DEGREE_RE.search(block)
    no_faculty = block.replace(fac.group(1), " ") if fac else block  # "Faculty of ... Artificial Intelligence" is not the major
    major = MAJOR_RE.search(no_faculty)
    mm = re.search(r"(?:Major|Department|Specialization)\s*[:\-]\s*([A-Za-z&' ]{3,40})", block)
    years = [int(y) for y in re.findall(r"(?<!\d)(20[0-3]\d)(?!\d)", block)]
    entry = {"university": uni.group(1).strip() if uni else "", "faculty": fac.group(1).strip() if fac else "",
             "degree": deg.group(1).strip() if deg else "",
             "major": (major.group(0).title() if major else (mm.group(1).strip() if mm else "")),
             "graduation_year": max(years) if years else None}
    return [entry] if any(v for v in entry.values()) else []


def _clean_title_line(line: str) -> str:
    line = re.sub(r"\(?\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}.*$", "", line, flags=re.I)
    line = re.sub(r"\(?\b\d{4}\s*[-–]\s*(?:\d{4}|Present|Current)\)?", "", line, flags=re.I)
    return line.strip(" ,|-–()")


def extract_experience(sections: dict, text: str) -> list:
    block = sections.get("experience", "")
    lines = [l.strip() for l in block.split("\n") if l.strip()]
    out = []
    for i, line in enumerate(lines):
        if line.startswith(BULLET) or len(line) > 110 or not TITLE_KW.search(line):
            continue
        clean = _clean_title_line(line)
        title, company = clean, ""
        parts = re.split(r"\s+at\s+|\s+[|–-]\s+|,\s+", clean, maxsplit=1)
        if len(parts) == 2:
            a, b = parts[0].strip(), parts[1].strip()
            title, company = (a, b) if TITLE_KW.search(a) or not TITLE_KW.search(b) else (b, a)
        elif i + 1 < len(lines) and not lines[i + 1].startswith(BULLET) and not TITLE_KW.search(lines[i + 1]) and len(lines[i + 1]) < 60:
            company = _clean_title_line(lines[i + 1])
        kind = "Internship" if re.search(r"intern", line, re.I) else "Volunteering" if re.search(r"volunteer", line, re.I) else "Job"
        out.append({"title": title[:80], "company": company[:80], "type": kind})
    return out


def extract_projects(sections: dict) -> dict:
    block = sections.get("projects", "")
    lines = [l.strip() for l in block.split("\n") if l.strip()]
    titles = [l.lstrip("".join(BULLET) + " ").strip() for l in lines if not l.startswith(BULLET) and len(l) <= 90 and len(l.split()) <= 12]
    bullets = [l for l in lines if l.startswith(BULLET)]
    count = len(titles) if titles else len(bullets)
    words = len(block.split())
    return {"count": count, "titles": titles[:8], "words": words, "avg_words": round(words / count) if count else 0}
