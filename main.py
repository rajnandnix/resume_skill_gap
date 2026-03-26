from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import (
    ALLOWED_ORIGINS,
    MAX_FILE_SIZE_BYTES,
    MAX_JOB_DESCRIPTION_LENGTH,
    APP_ENV,
    validate_settings,
)
from resume_parser import extract_resume_text
from skill_extractor import extract_skills
from skill_gap import extract_job_skills, find_skill_gap
from recommendations import generate_learning_plan

app = FastAPI()

validate_settings()

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


@app.get("/health")
def health():
    return {"status": "ok", "environment": APP_ENV}


# ✅ MAIN API ROUTE
@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
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
            error_text = str(ai_error).lower()
            if "insufficient_quota" in error_text or "exceeded your current quota" in error_text:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service quota exceeded. Please top up OpenAI billing or use a key with available credits."
                )
            if "invalid_api_key" in error_text:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service key is invalid. Please configure a valid OPENAI_API_KEY."
                )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI analysis service is temporarily unavailable. Please try again shortly."
            )

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