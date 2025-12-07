from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    db_url: str = os.getenv('DATABASE_URL')
    monitoring_system_url: str = os.getenv('MONITORING_SYSTEM_URL')
    allowed_origins: list[str] = os.getenv('ALLOWED_ORIGINS', '').split(',')

settings = Settings()