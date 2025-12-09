import uuid
import bcrypt
import smtplib
from email.message import EmailMessage
import asyncio
import logging
from core.settings import settings

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)

def gen_cid():
    return str(uuid.uuid4())

# async def send_email(to_email: str, subject: str, body: str):
#     """Send email notification. If email sending fails, log the error instead of crashing."""
#     sender_email = settings.sender_email
#     sender_password = settings.sender_password
#     smtp_server = settings.smtp_server
#     smtp_port = settings.smtp_port
#
#     # Skip email sending if credentials are not configured
#     if not sender_email or not sender_password:
#         logger.warning(f"Email credentials not configured. Skipping email to {to_email}")
#         logger.info(f"Would send email - To: {to_email}, Subject: {subject}, Body: {body}")
#         return
#
#     msg = EmailMessage()
#     msg["From"] = sender_email
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.set_content(body)
#
#     try:
#         loop = asyncio.get_running_loop()
#         await loop.run_in_executor(None, _send_sync_email, smtp_server, smtp_port, sender_email, sender_password, msg)
#         logger.info(f"Email sent successfully to {to_email}")
#     except Exception as e:
#         logger.error(f"Failed to send email to {to_email}: {e}")
#         # Don't raise the exception - just log it
#
# def _send_sync_email(smtp_server, smtp_port, sender_email, sender_password, msg):
#     with smtplib.SMTP(smtp_server, smtp_port) as smtp:
#         smtp.starttls()
#         smtp.login(sender_email, sender_password)
#         smtp.send_message(msg)
