__all__ = "settings"

import os

from pydantic_settings import BaseSettings
from functools import lru_cache


class S3(BaseSettings):
    class Config:
        env_file = ".env"
        env_prefix = "S3_"

    bucket: str = "bucket_name"
    tg_model_key: str = "model_weights"
    full_csv_key: str = "full_csv"


class UvicornURL(BaseSettings):
    """Represents Uvicorn settings"""

    class Config:
        env_prefix = "UVICORN_"

    host: str = "127.0.0.1"
    port: str = "8000"


class ProjectSettings(BaseSettings):
    """Represents Project settings"""

    class Config:
        env_prefix = "SETTINGS_"

    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_name: str = "fastapi_base"


class Settings(BaseSettings):
    api: UvicornURL = UvicornURL()
    project: ProjectSettings = ProjectSettings()
    s3: S3 = S3()


@lru_cache
def get_settings() -> Settings:
    """Singleton"""
    return Settings()


settings = get_settings()
