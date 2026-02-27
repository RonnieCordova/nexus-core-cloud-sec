import os
from dataclasses import dataclass


def _split_csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


@dataclass
class Settings:
    app_name: str
    app_env: str
    app_host: str
    app_port: int
    db_path: str
    aws_external_id_prefix: str
    cors_origins: list[str]
    allowed_hosts: list[str]
    debug_errors: bool


settings = Settings(
    app_name=os.getenv("APP_NAME", "Nexus Core Security API"),
    app_env=os.getenv("APP_ENV", "development"),
    app_host=os.getenv("APP_HOST", "0.0.0.0"),
    app_port=int(os.getenv("APP_PORT", "8000")),
    db_path=os.getenv("DB_PATH", "./nexus.db"),
    aws_external_id_prefix=os.getenv("AWS_EXTERNAL_ID_PREFIX", "nexus"),
    cors_origins=_split_csv(os.getenv("CORS_ORIGINS", "http://localhost:3000")),
    allowed_hosts=_split_csv(os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")),
    debug_errors=os.getenv("DEBUG_ERRORS", "false").lower() == "true",
)
