"""
Centralized configuration management for VeriClip AI.
All settings loaded from environment variables with sensible defaults for local dev.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "VeriClip AI"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False

    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = "vericlip-ai-2026"
    GOOGLE_CLOUD_REGION: str = "asia-south1"

    # Firebase
    FIREBASE_PROJECT_ID: str = "vericlip-ai-2026"
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None

    # Gemini / Vertex AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL_FINGERPRINT: str = "gemini-2.0-flash"
    GEMINI_MODEL_VERIFY: str = "gemini-2.5-pro"

    # Custom Search (for scanner agent)
    CUSTOM_SEARCH_API_KEY: Optional[str] = None
    CUSTOM_SEARCH_ENGINE_ID: Optional[str] = None

    # Pub/Sub
    PUBSUB_SCAN_TOPIC: str = "vericlip-scan-jobs"
    PUBSUB_VERIFY_TOPIC: str = "vericlip-verify-jobs"
    PUBSUB_ALERT_TOPIC: str = "vericlip-alerts"

    # Cloud Storage
    MEDIA_BUCKET: str = "vericlip-media-official"
    THREAT_EVIDENCE_BUCKET: str = "vericlip-threats-evidence"

    # C2PA
    C2PA_SIGNING_KEY_PATH: Optional[str] = None
    C2PA_CERT_PATH: Optional[str] = None

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_bool(cls, v):
        """Handle non-boolean DEBUG values (e.g., 'release' from Windows env)."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on", "debug")
        return bool(v)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton instance
settings = Settings()
