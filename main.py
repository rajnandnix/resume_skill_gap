from fastapi import FastAPI, UploadFile, Form, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS, MAX_FILE_SIZE_BYTES, MAX_JOB_DESCRIPTION_LENGTH
from resume_parser import extract_resume_text
from skill_extractor import extract_skills
from skill_gap import extract_job_skills, find_skill_gap
from recommendations import generate_learning_plan

app = FastAPI()

# ✅ Serve frontend (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# ✅ Home route → opens your UI
@app.get("/")
def home():
    return FileResponse("static/index.html")


# ✅ MAIN API ROUTE
@app.post("/analyze")
async def analyze_resume(
    file: UploadFile,
    job_description: str = Form(...)
):
    try:
        content_type = (file.content_type or "").lower()
        filename = (file.filename or "").lower()
        if "pdf" not in content_type and not filename.endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed."
            )

        trimmed_jd = (job_description or "").strip()
        if not trimmed_jd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is required."
            )
        if len(trimmed_jd) > MAX_JOB_DESCRIPTION_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job description is too long (max {MAX_JOB_DESCRIPTION_LENGTH} chars)."
            )

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File is too large. Max size allowed is {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )

        # 📄 Step 1: Extract text from resume
        resume_text = extract_resume_text(file.file)
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from this PDF. Please upload a text-based resume PDF."
            )

        # 🧠 Step 2: Extract skills from resume
        resume_skills = extract_skills(resume_text)

        # 💼 Step 3: Extract skills from job description
        job_skills = extract_job_skills(trimmed_jd)

        # ⚖️ Step 4: Compare skills
        missing_skills = find_skill_gap(resume_skills, job_skills)

        # 🤖 Step 5: Generate AI recommendations
        try:
            ai_report = generate_learning_plan(
                resume_text=resume_text,
                job_description=trimmed_jd,
                resume_skills=resume_skills,
                job_skills=job_skills,
                missing_skills=missing_skills
            )
        except Exception as ai_error:
            print("OpenAI Error:", ai_error)
            ai_report = {
                "profile_summary": [
                    "AI analysis is currently unavailable.",
                    "Please check OPENAI_API_KEY and try again."
                ],
                "required_skills": job_skills,
                "strengths": resume_skills[:6],
                "gap_areas": missing_skills[:8],
                "roadmap": {
                    "week_1_2": ["Review core role concepts and required tools."],
                    "week_3_4": ["Complete one guided project using missing skills."],
                    "month_2_3": ["Build and publish portfolio projects with measurable outcomes."]
                },
                "resources": ["Official documentation", "Role-specific beginner-to-advanced course"],
                "projects": ["End-to-end portfolio project aligned to the role"],
                "interview_tips": ["Prepare STAR stories", "Practice role-specific technical questions"],
                "top_next_actions": [
                    "Set up API key",
                    "Re-run analysis",
                    "Prioritize top 3 missing skills",
                    "Create a 4-week study plan",
                    "Build one project"
                ]
            }

        # 📦 Step 6: Return output
        return {
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "missing_skills": missing_skills,
            "ai_report": ai_report
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Server Error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while processing your request."
        )