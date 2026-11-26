"""Role keyword matching: weighted skill overlap + TF-IDF text similarity (scikit-learn / NumPy)."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data.job_requirements import JOB_ROLES, ROLE_NAMES


def _role_doc(role: dict) -> str:
    return " ".join(role["required"] * 2 + role["preferred"] + role["related"] + role["keywords"])


def _overlap(cv_skills: set, role: dict) -> float:
    total = 2 * len(role["required"]) + len(role["preferred"])
    got = 2 * sum(s in cv_skills for s in role["required"]) + sum(s in cv_skills for s in role["preferred"])
    return round(100 * got / total) if total else 0


def text_similarities(cv_text: str) -> dict:
    """TF-IDF cosine similarity (0-100) between the CV text and every role description."""
    docs = [cv_text] + [_role_doc(JOB_ROLES[r]) for r in ROLE_NAMES]
    tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True, token_pattern=r"(?u)\b[\w+#.]+\b")
    matrix = tfidf.fit_transform(docs)
    sims = cosine_similarity(matrix[0], matrix[1:]).ravel()
    return {r: int(round(float(v) * 100)) for r, v in zip(ROLE_NAMES, np.clip(sims, 0, 1))}


def match_role(cv_text: str, skill_names: list, role_name: str) -> dict:
    role, cv_skills, low = JOB_ROLES[role_name], set(skill_names), cv_text.lower()
    skills_low = {s.lower() for s in skill_names}
    required_hit = [s for s in role["required"] if s in cv_skills]
    preferred_hit = [s for s in role["preferred"] if s in cv_skills]
    return {
        "compatibility": _overlap(cv_skills, role),
        "matched": required_hit + preferred_hit,
        "missing_required": [s for s in role["required"] if s not in cv_skills],
        "missing_preferred": [s for s in role["preferred"] if s not in cv_skills],
        "relevant": [s for s in role["related"] if s in cv_skills],
        "suggested_keywords": [k for k in role["keywords"] if k not in low and k not in skills_low],
        "text_similarity": text_similarities(cv_text)[role_name],
        "all_roles": {r: _overlap(cv_skills, JOB_ROLES[r]) for r in ROLE_NAMES},
    }
