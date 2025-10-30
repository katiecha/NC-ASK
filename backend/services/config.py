"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path
from typing import List, Optional
import json


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENVIRONMENT: str = "development"

    # Supabase Configuration (PLACEHOLDER - to be configured)
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your_anon_key_here"
    SUPABASE_SERVICE_ROLE_KEY: str = "your_service_role_key_here"

    # AI Services (PLACEHOLDER - to be configured)
    GOOGLE_API_KEY: str = "your_gemini_api_key_here"

    # Security
    SECRET_KEY: str = "your-secret-key-for-session-signing-change-in-production"
    ALLOWED_ORIGINS: Optional[str] = None
    
    @property
    def allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from string or return defaults"""
        if self.ALLOWED_ORIGINS:
            try:
                return json.loads(self.ALLOWED_ORIGINS)
            except json.JSONDecodeError:
                # If it's a comma-separated string
                return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:3000",
            "http://localhost:8000"
        ]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    MAX_QUERY_LENGTH: int = 500

    # RAG Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    TOP_K_RETRIEVAL: int = 5
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # LLM Configuration
    LLM_MODEL: str = "gemini-1.5-flash"
    MAX_CONTEXT_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.3

    # Feature Flags
    ENABLE_EMAIL_EXPORT: bool = False
    ENABLE_QUERY_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(
        extra='ignore',
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        case_sensitive=True
    )


# Create global settings instance
settings = Settings()