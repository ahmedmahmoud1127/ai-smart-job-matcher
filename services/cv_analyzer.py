"""Orchestrates the full CV analysis from extracted text."""
from data.job_requirements import ROLE_NAMES
from services import cv_parser as P
from services.cv_scoring import explain, score_cv
from services.keyword_matcher import match_role
from services.recommendations import build_feedback
from services.skills_extractor import find_skills, group_by_category


def analyze_cv(text: str, role: str) -> dict:
    if role not in ROLE_NAMES:
        raise ValueError(f"Unknown role: {role}")
    sections = P.split_sections(text)
    contact = P.extract_contact(text)
    skills = find_skills(text)
    education = P.extract_education(sections, text)
    experience = P.extract_experience(sections, text)
    projects = P.extract_projects(sections)
    cert_kw = bool(sections.get("certifications")) or bool(P.re.search(r"\b(certified|certificate|certification|coursera|udemy|edx)\b", text, P.re.I))
    present = {
        "contact": bool(contact["email"] or contact["phone"]),
        "summary": bool(sections.get("summary")),
        "education": bool(sections.get("education")) or bool(education),
        "skills": bool(sections.get("skills")) or len(skills) >= 3,
        "experience": bool(sections.get("experience")) or bool(experience),
        "projects": bool(sections.get("projects")) or projects["count"] > 0,
        "certifications": cert_kw,
        "languages": bool(sections.get("languages")),
    }
    keywords = match_role(text, [s["name"] for s in skills], role)
    score = score_cv(present, skills, education, experience, projects, len(sections.get("experience", "").split()), keywords["compatibility"])
    result = {"role": role, "word_count": len(text.split()), "contact": contact, "skills": skills,
              "skills_by_category": group_by_category(skills), "education": education, "experience": experience,
              "projects": projects, "sections": present, "keywords": keywords, "score": score, "text": text}
    result.update(build_feedback(result))
    result["score"]["explanation"] = explain(score)
    result["stats"] = {"skills_found": len(skills), "strengths": len(result["strengths"]),
                       "improvements": len(result["improvements"]), "keywords_pct": keywords["compatibility"]}
    del result["text"]  # the full text is stored separately in its own DB column
    return result
