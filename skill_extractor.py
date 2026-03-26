import re

CANONICAL_SKILLS = {
    "python": {"python"},
    "machine learning": {"machine learning", "ml"},
    "sql": {"sql", "postgresql", "mysql", "sqlite"},
    "excel": {"excel", "ms excel", "microsoft excel"},
    "power bi": {"power bi", "powerbi"},
    "tableau": {"tableau"},
    "statistics": {"statistics", "statistical analysis"},
    "data analysis": {"data analysis", "data analytics"},
    "pandas": {"pandas"},
    "numpy": {"numpy"},
    "matplotlib": {"matplotlib"},
    "scikit-learn": {"scikit-learn", "sklearn"},
}


def extract_skills(text):
    content = (text or "").lower()
    found_skills = []

    for skill, aliases in CANONICAL_SKILLS.items():
        if any(re.search(r"\b" + re.escape(alias) + r"\b", content) for alias in aliases):
            found_skills.append(skill)

    return sorted(found_skills)