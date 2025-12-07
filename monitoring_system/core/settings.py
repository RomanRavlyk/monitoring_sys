from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    db_url: str = os.getenv("DATABASE_URL")


settings = Settings()
