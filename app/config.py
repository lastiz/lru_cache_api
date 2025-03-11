from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="APP_", extra="ignore")

    cache_capacity: int
    port: int

    # logging
    log_level: str
    log_format: str = "%(name)s | %(asctime)s | %(levelname)s | %(message)s"
    logs_path: str = "/logs"
