import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_JOB_DESCRIPTION_LENGTH = int(os.getenv("MAX_JOB_DESCRIPTION_LENGTH", "4000"))

# Comma-separated values, e.g. http://localhost:8000,http://127.0.0.1:8000
_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
ALLOWED_ORIGINS = [origin.strip() for origin in _origins.split(",") if origin.strip()]


def validate_settings():
    if APP_ENV.lower() == "production":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be configured in production.")
        if not ALLOWED_ORIGINS:
            raise ValueError("ALLOWED_ORIGINS must be configured in production.")
