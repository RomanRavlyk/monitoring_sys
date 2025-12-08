from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    db_url: str = os.getenv('DATABASE_URL')
    monitoring_system_url: str = os.getenv('MONITORING_SYSTEM_URL')
    allowed_origins: str = os.getenv('ALLOWED_ORIGINS')
    client_id: str = os.getenv('CLIENT_ID')

settings = Settings()