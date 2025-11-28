import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # DataForSEO API Settings
    dataforseo_login: str = Field(..., env="DATAFORSEO_LOGIN")
    dataforseo_password: str = Field(..., env="DATAFORSEO_PASSWORD")
    dataforseo_base_url: str = "https://api.dataforseo.com/v3"
    dataforseo_sandbox_url: str = "https://sandbox.dataforseo.com/v3"

    # Geocoding API Settings
    google_maps_api_key: Optional[str] = Field(None, env="GOOGLE_MAPS_API_KEY")
    opencage_api_key: Optional[str] = Field(None, env="OPENCAGE_API_KEY")

    # Application Settings
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")
    api_host: str = Field("127.0.0.1", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")

    # Rate Limiting Settings
    max_requests_per_minute: int = Field(60, env="MAX_REQUESTS_PER_MINUTE")
    batch_size: int = Field(10, env="BATCH_SIZE")

    # Default API Settings
    default_language: str = Field("en", env="DEFAULT_LANGUAGE")
    default_device: str = Field("desktop", env="DEFAULT_DEVICE")
    default_depth: int = Field(40, env="DEFAULT_DEPTH")

    # Timeout Settings
    request_timeout: int = 30
    retry_attempts: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def dataforseo_url(self) -> str:
        # Use sandbox for development, production API for live
        if self.is_development:
            return self.dataforseo_sandbox_url
        return self.dataforseo_base_url

# Create global settings instance
settings = Settings()