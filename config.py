import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fitcoach-ai-super-secret-key-2025")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "fitcoach.db"))
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
