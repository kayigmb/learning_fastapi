from pydantic_settings import BaseSettings, SettingsConfigDict


class settings(BaseSettings):
    DB_URL: str
    REDIS_URL: str
    ALGORITHM: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str

    model_config = SettingsConfigDict(env_file=".env")


settings = settings()
