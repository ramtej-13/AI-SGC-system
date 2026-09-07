import os
from pydantic_settings import BaseSettings

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_DB = f"sqlite:///{os.path.join(_BASE_DIR, 'sgc.db').replace(chr(92), '/')}"

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Based Student Grievance Classification and Smart Routing System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "super-secret-key-for-college-ai-sgc-system-development-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # SQLite Database
    DATABASE_URL: str = _DEFAULT_DB
    
    # Confidence threshold for ML fallback
    CONFIDENCE_THRESHOLD: float = 0.70
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    class Config:
        case_sensitive = True

settings = Settings()
