import re

CANONICAL_SKILLS = {
    "python": {"python"},
    "sql": {"sql", "postgresql", "mysql", "sqlite"},
    "machine learning": {"machine learning", "ml"},
    "deep learning": {"deep learning"},
    "data analysis": {"data analysis", "data analytics"},
    "pandas": {"pandas"},
    "numpy": {"numpy"},
    "power bi": {"power bi", "powerbi"},
    "tableau": {"tableau"},
    "excel": {"excel", "ms excel", "microsoft excel"},
    "statistics": {"statistics", "statistical analysis"},
    "nlp": {"nlp", "natural language processing"},
    "tensorflow": {"tensorflow"},
    "pytorch": {"pytorch"},
    "communication": {"communication", "stakeholder management"},
    "data visualization": {"data visualization", "visualization"},
}

ROLE_SKILL_TEMPLATES = {
    "data analyst": [
        "sql", "excel", "python", "statistics", "data visualization", "power bi"
    ],
    "data scientist": [
        "python", "sql", "machine learning", "statistics", "pandas", "numpy"
    ],
    "ml engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch"
    ],
}


def extract_job_skills(job_description):
    content = (job_description or "").lower()
    extracted = set()

    for skill, aliases in CANONICAL_SKILLS.items():
        if any(re.search(r"\b" + re.escape(alias) + r"\b", content) for alias in aliases):
            extracted.add(skill)

    # Infer expected skills from generic role names
    for role, skills in ROLE_SKILL_TEMPLATES.items():
        if role in content:
            extracted.update(skills)

    return sorted(extracted)


def find_skill_gap(resume_skills, job_skills):
    resume_set = set(resume_skills or [])
    return sorted([skill for skill in (job_skills or []) if skill not in resume_set])