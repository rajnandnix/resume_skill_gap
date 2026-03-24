import os
import json
from openai import OpenAI
from config import OPENAI_MODEL

def generate_learning_plan(
    resume_text,
    job_description,
    resume_skills,
    job_skills,
    missing_skills
):

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Add it as an environment variable before running the app."
        )

    client = OpenAI(api_key=api_key)

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
    return json.loads(raw_content)