from sqlalchemy.exc import SQLAlchemyError
import asyncio

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
)
