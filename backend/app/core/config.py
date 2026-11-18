from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Diving Club Manager"
    app_env: str = "development"
    database_url: str = "sqlite:///./diving_club.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
