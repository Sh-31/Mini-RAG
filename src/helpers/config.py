from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    HUGGFACE_API_KEY: str

    FILE_ALLOWED_TYPES: list
    File_MAX_SIZE: int
    FILE_DEFAULT_CHECK_SIZE: int

    class Config:
        env_file = ".env"
      
def get_settings():
    return Settings()
