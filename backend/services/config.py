"""
Configuration management using Pydantic Settings
"""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENVIRONMENT: str = "development"

    # Supabase Configuration (PLACEHOLDER - to be configured)
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your_anon_key_here"
    SUPABASE_SERVICE_ROLE_KEY: str = "your_service_role_key_here"

    # OpenShift AI Services (PLACEHOLDER - to be configured)
    # NOTE: Base URLs should NOT include /v1 suffix (added automatically by OpenAI SDK)
    OPENSHIFT_API_KEY: str = "your_openshift_llm_api_key_here"
    OPENSHIFT_BASE_URL: str = "https://your-openshift-llm-endpoint.com"
    OPENSHIFT_EMBEDDING_API_KEY: str = "your_openshift_embedding_api_key_here"
    OPENSHIFT_EMBEDDING_BASE_URL: str = "https://your-openshift-embedding-endpoint.com"

    # Security
    SECRET_KEY: str = "your-secret-key-for-session-signing-change-in-production"
    ALLOWED_ORIGINS: str | None = None

    @property
    def allowed_origins(self) -> list[str]:
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
    EMBEDDING_MODEL: str = "bge-large"  # BGE-large deployed on OpenShift
    EMBEDDING_DIMENSION: int = 1024  # BGE-large dimension (was 384 for all-MiniLM-L6-v2)
    TOP_K_RETRIEVAL: int = 5
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # LLM Configuration
    LLM_MODEL: str = "granite-31-8b-instruct-quantize-w8a8"  # Model name from OpenShift deployment
    MAX_CONTEXT_TOKENS: int = 8000
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
