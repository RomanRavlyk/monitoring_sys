from fastapi import FastAPI, Request, HTTPException, Depends, APIRouter
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.failure_log import router as failure_log_router
import logging
from services.api_key import APIKeyService
from exceptions.api_key import ApiKeyException
from exceptions.failure_log import FailureLogException
from services.failure_log import FailureLogService
from db.database import get_db
import traceback
from models.failure_log import FailureLog
from middleware import APIKeyMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server up...")
    yield
    logger.info("Shutting server down...")


app = FastAPI(lifespan=lifespan)

dev_exc_router = APIRouter(prefix="/dev", tags=["Developer Exceptions"])
devops_exc_router = APIRouter(prefix="/devops", tags=["DevOps Exceptions"])
random_exc_router = APIRouter(prefix="/random", tags=["Random Exceptions"])

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

app.add_middleware(APIKeyMiddleware)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    custom_exc = (isinstance(exc, ApiKeyException) or isinstance(exc, FailureLogException))
    try:
        async for db in get_db():
            trace_back = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))

            failure_log = FailureLog(
                error_message=str(exc),
                error_traceback=trace_back,
                error_type=type(exc).__name__,
                error_status_code=exc.status_code if custom_exc or isinstance(exc, HTTPException) else 500,
            )

            failure_log = await FailureLogService.analise_exception(exc, failure_log)

            db.add(failure_log)
            await db.commit()
            await db.refresh(failure_log)

            logger.error(
                f"Exception occurred, logged to failure_log table: {type(exc).__name__}: {str(exc)}")

            return JSONResponse(status_code = failure_log.error_status_code, content=failure_log.error_message)

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error (no DB session)"},
        )

    except Exception as log_exc:
        logger.error(f"Failed to log exception to failure_log table: {str(log_exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

    #
    # logger.exception(f"An unexpected error occurred: {str(exc)}")
    # raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/imitate_value_error")
async def imitate_value_error():
    raise ValueError("This is a simulated ValueError for testing purposes.")

# ============= DEVELOPER EXCEPTIONS =============

@dev_exc_router.get("/syntax-error")
async def dev_syntax_error():
    """Imitation of SyntaxError"""
    code = "def invalid syntax here"
    compile(code, '<string>', 'exec')
    return {"status": "ok"}

@dev_exc_router.get("/type-error")
async def dev_type_error():
    """Imitation of TypeError - Incorrect data type"""
    result = "string" + 123
    return {"result": result}

@dev_exc_router.get("/key-error")
async def dev_key_error():
    """Imitation KeyError - key in dict not found"""
    data = {"name": "John", "age": 30}
    value = data["nonexistent_key"]
    return {"value": value}

@dev_exc_router.get("/index-error")
async def dev_index_error():
    """Imitation IndexError - index out of range"""
    my_list = [1, 2, 3]
    value = my_list[10]
    return {"value": value}

@dev_exc_router.get("/attribute-error")
async def dev_attribute_error():
    """Imitation AttributeError - attribute not found"""
    obj = {"key": "value"}
    obj.nonexistent_method()
    return {"status": "ok"}

# ============= DEVOPS EXCEPTIONS =============

@devops_exc_router.get("/file-not-found")
async def devops_file_not_found():
    """Imitation FileNotFoundError - file not found"""
    with open("/nonexistent/path/to/file.txt", "r") as f:
        content = f.read()
    return {"content": content}

@devops_exc_router.get("/permission-error")
async def devops_permission_error():
    """Imitation PermissionError - permission denied"""
    import os
    os.chmod("/root/protected_file.txt", 0o000)
    with open("/root/protected_file.txt", "w") as f:
        f.write("test")
    return {"status": "ok"}

@devops_exc_router.get("/connection-error")
async def devops_connection_error():
    """Imitation ConnectionError - impossible to create a network connection"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect(("192.0.2.1", 9999))  # Non-routable IP
    return {"status": "connected"}

@devops_exc_router.get("/timeout-error")
async def devops_timeout_error():
    """Imitation TimeoutError - operation timed out"""
    import asyncio
    await asyncio.wait_for(asyncio.sleep(10), timeout=0.1)
    return {"status": "ok"}

@devops_exc_router.get("/runtime-error")
async def devops_runtime_error():
    """Imitation RuntimeError - maximum recursion depth exceeded"""
    def recursive_function(depth=0):
        if depth < 1000:
            return recursive_function(depth + 1)
        raise RuntimeError("Maximum recursion depth exceeded in comparison")

    recursive_function()
    return {"status": "ok"}

# ============= RANDOM/OTHER EXCEPTIONS =============

@random_exc_router.get("/buffer-error")
async def random_buffer_error():
    """Imitation BufferError - buffer error"""
    import array
    arr = array.array('i', [1, 2, 3])
    mv = memoryview(arr)

    arr.append(4)
    mv[0] = 10
    raise BufferError("Cannot modify buffer with exported pointers")

@random_exc_router.get("/encoding-error")
async def random_encoding_error():
    """Imitation LookupError - encoding not found"""
    text = "Hello"

    encoded = text.encode('nonexistent_encoding')
    return {"encoded": encoded}

@random_exc_router.get("/warning-error")
async def random_warning_error():
    """Imitation UserWarning as exception"""
    import warnings
    warnings.simplefilter('error')  # Перетворюємо warnings на exceptions
    warnings.warn("This is a user warning raised as exception", UserWarning)
    return {"status": "ok"}

@random_exc_router.get("/system-error")
async def random_system_error():
    """Imitation SystemError - internal error in the interpreter"""
    raise SystemError("Internal error in Python interpreter simulation")

@random_exc_router.get("/interrupt-error")
async def random_interrupt_error():
    """Imitation KeyboardInterrupt"""
    import signal
    import os
    # Simulate KeyboardInterrupt
    raise KeyboardInterrupt("Simulated keyboard interrupt")

@app.post("/imitate_key_creating_exc")
async def imitate_key_creating_exc(api_key: str, db: AsyncSession = Depends(get_db)):
    apikey_service = APIKeyService(db)
    await apikey_service.add_api_key_to_db(api_key)
    return {"status": "API key added successfully."}

app.include_router(failure_log_router)
app.include_router(dev_exc_router)
app.include_router(devops_exc_router)
app.include_router(random_exc_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app")
