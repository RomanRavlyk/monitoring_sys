from fastapi import FastAPI
from contextlib import asynccontextmanager
from failure_log.api import router as failure_log_router
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting server up...")
    yield
    print("Shutting server down...")

app = FastAPI(lifespan=lifespan)
app.include_router(failure_log_router)
@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app")