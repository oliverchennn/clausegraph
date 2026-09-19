"""Server-only configuration; defaults are explicitly local development."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

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
    text_provider: Literal["nvidia", "brev"] = "nvidia"
    brev_nim_base_url: str = "http://127.0.0.1:18000/v1"
    brev_nim_model: str = ""
    evidence_provider: Literal["nvidia", "gemini"] = "nvidia"
    nvidia_evidence_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    nvidia_evidence_reasoning_budget: int = Field(default=1024, ge=0, le=4096)
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
    def text_model(self) -> str:
        return self.brev_nim_model if self.text_provider == "brev" else self.nvidia_model

    @property
    def text_configured(self) -> bool:
        return bool(self.brev_nim_model.strip()) if self.text_provider == "brev" else bool(self.nvidia_api_key)

    @property
    def processing_route(self) -> str:
        """Pin consented queued work to destinations/models, without persisting secrets."""
        text_url = self.brev_nim_base_url if self.text_provider == "brev" else self.nvidia_base_url
        evidence_url = self.nvidia_base_url if self.evidence_provider == "nvidia" else self.gemini_base_url
        evidence_model = self.nvidia_evidence_model if self.evidence_provider == "nvidia" else self.gemini_model
        return sha256(repr((self.text_provider, text_url.rstrip('/'), self.text_model,
                           self.evidence_provider, evidence_url.rstrip('/'), evidence_model)).encode()).hexdigest()

    @model_validator(mode="after")
    def brev_requires_private_tunnel(self):
        url = urlsplit(self.brev_nim_base_url)
        if (url.scheme != "http" or url.hostname not in ("127.0.0.1", "localhost", "::1")
                or url.username is not None or url.password is not None or url.query or url.fragment
                or url.path.rstrip('/') != "/v1"):
            raise ValueError("BREV_NIM_BASE_URL must be a loopback HTTP /v1 endpoint through a private SSH tunnel")
        return self

    @property
    def spaces_configured(self) -> bool:
        return all((self.spaces_endpoint, self.spaces_bucket,
                    self.spaces_access_key_id, self.spaces_secret_access_key))

    @model_validator(mode="after")
    def production_requires_durable_services(self):
        longest_call = ((self.provider_timeout_seconds + 10) * (self.provider_retries + 1)
                        + sum(min(2 ** attempt, 4) for attempt in range(self.provider_retries)) + 25)
        if self.job_lease_seconds <= longest_call:
            raise ValueError("JOB_LEASE_SECONDS must exceed one bounded provider call including retries/connect time and PDF rendering")
        if self.environment == "production":
            if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
                raise ValueError("Production requires PostgreSQL DATABASE_URL and explicit migrations")
            if not self.spaces_configured:
                raise ValueError("Production requires private Spaces storage configuration")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
