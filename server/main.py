from fastapi import FastAPI, Request, HTTPException, Depends
from contextlib import asynccontextmanager

from starlette.responses import JSONResponse

from api.failure_log import router as failure_log_router
import logging
from services.failure_log import FailureLogService
from db.database import get_db
import traceback
from models.failure_log import FailureLog

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
# logging.getLogger('uvicorn.error').setLevel(logging.CRITICAL)
# logging.getLogger('uvicorn.access').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server up...")
    yield
    logger.info("Shutting server down...")

app = FastAPI(lifespan=lifespan)
app.include_router(failure_log_router)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    try:
        async for db in get_db():
            failure_log_service = FailureLogService(db)

            trace_back = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))

            failure_log = FailureLog(
                error_message=str(exc),
                error_traceback=trace_back,
                error_type=type(exc).__name__,
            )

            failure_log = await failure_log_service.analise_exception(exc, failure_log)

            db.add(failure_log)
            await db.commit()
            await db.refresh(failure_log)

            logger.error(f"Exception occurred, logged to failure_log table: {type(exc).__name__}: {str(exc)}")

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app")
