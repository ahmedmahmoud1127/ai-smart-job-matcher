"""Rule-based strengths, weaknesses and recommendations derived from the actual analysis."""
from services.cv_parser import MEASURE_RE, SECTION_LABELS


def build_feedback(a: dict) -> dict:
    """a = partial analysis dict (skills, education, experience, projects, sections, contact, keywords, word_count, text)."""
    skills, kw, proj = a["skills"], a["keywords"], a["projects"]
    tech = [s for s in skills if s["category"] != "Soft Skills"]
    cats = {s["category"] for s in skills}
    edu = a["education"][0] if a["education"] else {}
    S, W, R = [], [], []  # strengths, weaknesses, recommendations (ordered by priority)

    # ---- strengths
    if len(tech) >= 8:
        S.append(f"Good technical skills: {len(tech)} technical skills detected.")
    if len(cats) >= 4:
        S.append(f"Well-rounded profile covering {len(cats)} skill categories.")
    if edu.get("university") and edu.get("degree"):
        S.append("Clear educational information (university and degree).")
    if edu.get("major"):
        S.append(f"Relevant academic background: {edu['major']}.")
    if proj["count"] >= 2:
        S.append(f"Multiple projects listed ({proj['count']}).")
    if a["experience"]:
        S.append(f"Relevant experience: {len(a['experience'])} position(s) found.")
    if a["sections"]["summary"]:
        S.append("Includes a professional summary.")
    if a["contact"]["github"]:
        S.append("GitHub profile is included.")
    if kw["compatibility"] >= 70:
        S.append(f"Strong keyword overlap with {a['role']} ({kw['compatibility']}%).")
    if a["sections"]["certifications"]:
        S.append("Certifications or courses are listed.")

    # ---- weaknesses + recommendations
    for key in ("summary", "experience", "projects", "certifications", "languages", "skills"):
        if not a["sections"][key]:
            W.append(f"Missing section: {SECTION_LABELS[key]}.")
    if not a["sections"]["contact"]:
        W.append("No contact information (email or phone) found.")
    if not a["contact"]["github"]:
        W.append("No GitHub link found.")
    if not a["contact"]["linkedin"]:
        W.append("No LinkedIn link found.")
    if len(tech) < 5:
        W.append("Insufficient technical keywords detected.")
    if proj["count"] and proj["avg_words"] < 15:
        W.append("Limited project descriptions.")
    if not a["education"]:
        W.append("Education details could not be identified.")
    elif not edu.get("graduation_year"):
        W.append("Graduation year is missing.")
    if not MEASURE_RE.search(a["text"]):
        W.append("No measurable achievements found.")
    if kw["compatibility"] < 50:
        W.append(f"Low keyword overlap with {a['role']} ({kw['compatibility']}%).")
    if a["word_count"] < 150:
        W.append("The CV is very short.")
    elif a["word_count"] > 1000:
        W.append("The CV is very long; aim for 1-2 pages.")

    if not a["sections"]["summary"]:
        R.append("Add a 2-3 line professional summary stating your target role and strongest skills.")
    if kw["missing_required"]:
        R.append(f"For {a['role']} roles, add these core skills to your Skills section if you really have them: "
                 f"{', '.join(kw['missing_required'][:5])}. If you don't yet, consider learning them.")
    if proj["count"] == 0:
        R.append("Add 2-3 projects with the technologies used and a GitHub link.")
    elif proj["avg_words"] < 15:
        R.append("Expand each project with what you built, the technologies you used and the result.")
    if not MEASURE_RE.search(a["text"]):
        R.append("Include measurable achievements, e.g. 'reduced page load time by 30%' or 'built an API used by 200 students'.")
    if not a["contact"]["github"]:
        R.append("Add your GitHub profile link so employers can see your code.")
    if not a["contact"]["linkedin"]:
        R.append("Add your LinkedIn profile link.")
    if not a["sections"]["certifications"]:
        R.append("List relevant courses or certifications (e.g. from Coursera, Udemy or your university).")
    if kw["suggested_keywords"]:
        R.append(f"Where truthful, mention role keywords such as: {', '.join(kw['suggested_keywords'][:5])}.")
    if not a["experience"]:
        R.append("Add internships, volunteering or freelance work, even short ones, to show practical experience.")
    if not R:
        R.append("Your CV covers the main areas. Tailor it to each job description before applying.")
    return {"strengths": S, "improvements": W, "recommendations": R}
