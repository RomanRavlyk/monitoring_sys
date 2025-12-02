from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from core.settings import settings
from .base import Base

engine = create_async_engine(settings.db_url, echo=False, future=True)
async_session = AsyncSession(engine)

async def get_db():
    async with async_session as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
