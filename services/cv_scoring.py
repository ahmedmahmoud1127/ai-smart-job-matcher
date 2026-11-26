"""Estimated CV quality score (0-100). Not a guarantee of hiring or ATS acceptance."""
WEIGHTS = {"Structure": 25, "Skills": 20, "Education": 15, "Experience": 15, "Projects": 10, "Keywords": 15}


def score_cv(sections_present: dict, skills: list, education: list, experience: list, projects: dict,
             exp_words: int, keyword_pct: int) -> dict:
    tech = [s for s in skills if s["category"] != "Soft Skills"]
    cats = {s["category"] for s in skills}
    edu = education[0] if education else {}
    pts = {
        "Structure": WEIGHTS["Structure"] * sum(sections_present.values()) / max(len(sections_present), 1),
        "Skills": 14 * min(len(tech), 10) / 10 + 6 * min(len(cats), 4) / 4,
        "Education": 5 * bool(edu.get("university")) + 4 * bool(edu.get("degree")) + 3 * bool(edu.get("major")) + 3 * bool(edu.get("graduation_year")),
        "Experience": 10 * min(len(experience), 2) / 2 + 5 * min(exp_words, 80) / 80,
        "Projects": 6 * min(projects["count"], 3) / 3 + 4 * min(projects["avg_words"], 30) / 30,
        "Keywords": WEIGHTS["Keywords"] * keyword_pct / 100,
    }
    breakdown = {k: {"points": round(v, 1), "max": WEIGHTS[k]} for k, v in pts.items()}
    total = int(round(sum(pts.values())))
    return {"total": min(total, 100), "breakdown": breakdown, "label": label_for(total)}


def label_for(total: int) -> str:
    return ("Excellent CV!" if total >= 85 else "Good CV" if total >= 70 else "Fair CV - room to grow" if total >= 50
            else "Needs improvement")


def explain(score: dict) -> str:
    ratios = {k: v["points"] / v["max"] for k, v in score["breakdown"].items()}
    best, worst = max(ratios, key=ratios.get), min(ratios, key=ratios.get)
    return (f"Your estimated score is {score['total']}/100. Your strongest area is {best.lower()} "
            f"({round(ratios[best] * 100)}% of its points); the biggest opportunity is {worst.lower()} "
            f"({round(ratios[worst] * 100)}%).")
