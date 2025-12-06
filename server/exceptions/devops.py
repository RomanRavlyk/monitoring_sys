from sqlalchemy.exc import SQLAlchemyError
import asyncio
from exceptions.failure_log import FailureLogDatabaseError

DEVOPS_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
    FileNotFoundError,
    PermissionError,
    BrokenPipeError,
    ConnectionRefusedError,
    asyncio.TimeoutError,
    RuntimeError,
    SQLAlchemyError,
    FailureLogDatabaseError
)
