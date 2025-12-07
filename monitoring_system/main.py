import asyncio

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from schemas.failure_log import FailureLog

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

async def periodic_healthcheck():
    while True:
        logger.info("Performing periodic health check...")
        # Here you would add the actual health check logic
        await asyncio.sleep(300)  # Sleep for 5 minutes



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server up...")
    yield
    logger.info("Shutting server down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/failure_log")
async def create_failure_log(failure_log: FailureLog):
    logger.info(f"Received failure log: {failure_log}")
    return {"message": "Failure log received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)