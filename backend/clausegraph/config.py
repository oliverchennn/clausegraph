"""Server-only configuration; defaults are explicitly local development."""
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    environment: str = "development"
    database_url: str = "sqlite:///./.data/clausegraph.db"
    local_storage_path: Path = Path(".data/documents")
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1024, le=25 * 1024 * 1024)
    provider_timeout_seconds: float = Field(default=40, gt=0, le=120)
    provider_retries: int = Field(default=2, ge=0, le=3)
    worker_poll_seconds: float = Field(default=1, gt=0, le=30)
    job_lease_seconds: int = Field(default=300, ge=60, le=1800)
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "nvidia/nemotron-3.5-lightning-30b-a3b"
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-3.8-flash"
    elevenlabs_api_key: str = ""
    elevenlabs_base_url: str = "https://api.elevenlabs.io/v1"
    elevenlabs_stt_model: str = "scribe_v2"
    elevenlabs_tts_model: str = "eleven_multilingual_v2"
    elevenlabs_voice_id: str = ""
    spaces_endpoint: str = ""
    spaces_region: str = "nyc3"
    spaces_bucket: str = ""
    spaces_access_key_id: str = ""
    spaces_secret_access_key: str = ""

    @property
    def spaces_configured(self) -> bool:
        return all((self.spaces_endpoint, self.spaces_bucket,
                    self.spaces_access_key_id, self.spaces_secret_access_key))

    @model_validator(mode="after")
    def production_requires_durable_services(self):
        longest_call = ((self.provider_timeout_seconds + 10) * (self.provider_retries + 1)
                        + sum(min(2 ** attempt, 4) for attempt in range(self.provider_retries)) + 5)
        if self.job_lease_seconds <= longest_call:
            raise ValueError("JOB_LEASE_SECONDS must exceed one bounded provider call including retries/connect time")
        if self.environment == "production":
            if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
                raise ValueError("Production requires PostgreSQL DATABASE_URL and explicit migrations")
            if not self.spaces_configured:
                raise ValueError("Production requires private Spaces storage configuration")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
