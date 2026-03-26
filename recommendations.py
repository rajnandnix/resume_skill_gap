import json
from openai import OpenAI
from config import OPENAI_MODEL, OPENAI_API_KEY

def generate_learning_plan(
    resume_text,
    job_description,
    resume_skills,
    job_skills,
    missing_skills
):

    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI service is not configured."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Keep prompt size controlled for long resumes
    trimmed_resume_text = (resume_text or "")[:6000]

    prompt = f"""
You are an expert career mentor and hiring coach.

Candidate resume text:
{trimmed_resume_text}

Target job description:
{job_description}

Rule-based extracted resume skills:
{resume_skills}

Rule-based extracted job skills:
{job_skills}

Rule-based missing skills:
{missing_skills}

Return only valid JSON with this exact shape:
{{
  "profile_summary": ["point1", "point2", "point3"],
  "required_skills": ["skill1", "skill2"],
  "strengths": ["point1", "point2"],
  "gap_areas": ["point1", "point2"],
  "roadmap": {{
    "week_1_2": ["task1", "task2"],
    "week_3_4": ["task1", "task2"],
    "month_2_3": ["task1", "task2"]
  }},
  "resources": ["resource1", "resource2", "resource3"],
  "projects": ["project idea 1", "project idea 2"],
  "interview_tips": ["tip1", "tip2", "tip3"],
  "top_next_actions": ["action1", "action2", "action3", "action4", "action5"]
}}

Rules:
- Keep each string concise and actionable.
- Make outputs specific to the target role.
- If JD is generic, infer practical skills expected for that role.
- Prioritize readability and real-world execution.
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        response_format={"type": "json_object"}
    )

    raw_content = response.choices[0].message.content
    parsed = json.loads(raw_content)

    # Enforce consistent response shape for frontend rendering
    return {
        "profile_summary": parsed.get("profile_summary", []),
        "required_skills": parsed.get("required_skills", []),
        "strengths": parsed.get("strengths", []),
        "gap_areas": parsed.get("gap_areas", []),
        "roadmap": {
            "week_1_2": parsed.get("roadmap", {}).get("week_1_2", []),
            "week_3_4": parsed.get("roadmap", {}).get("week_3_4", []),
            "month_2_3": parsed.get("roadmap", {}).get("month_2_3", [])
        },
        "resources": parsed.get("resources", []),
        "projects": parsed.get("projects", []),
        "interview_tips": parsed.get("interview_tips", []),
        "top_next_actions": parsed.get("top_next_actions", [])
    }