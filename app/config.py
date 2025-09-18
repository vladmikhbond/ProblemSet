from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    PSS_HOST: str 

    class Config:
        env_file = "/.env"
        env_file_encoding = "utf-8"

# створюємо один глобальний екземпляр
settings = Settings()