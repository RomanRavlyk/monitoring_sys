from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    db_url: str = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL")
    # sender_email: str = os.getenv("SENDER_EMAIL")
    # smtp_server: str = os.getenv("SMTP_SERVER")
    # smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    # sender_password: str = os.getenv("EMAIL_PASSWORD")

settings = Settings()
