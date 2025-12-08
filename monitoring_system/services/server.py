from sqlalchemy.ext.asyncio import AsyncSession
from models.server import Server
from sqlalchemy.exc import SQLAlchemyError
# from exceptions.server import ServerDatabaseError
import logging
from sqlalchemy import select
from utils import gen_cid

logger = logging.getLogger(__name__)


class ServerService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @property
    def db(self):
        return self._db


    async def create_server(self, data: dict):
        try:
            new_server = Server(**data)
            new_server.alerts = []
            new_server.client_id = gen_cid()
            self.db.add(new_server)
            await self.db.commit()
            await self.db.refresh(new_server)
            return new_server
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Error creating server: {str(e)}")
            raise


    async def get_server_by_id(self, id: int) -> Server | None:
        try:
            result = await self.db.execute(
                select(Server).where(Server.id == id)
            )
            server = result.scalars().first()
            return server
        except SQLAlchemyError as e:
            logger.exception(f"Error retrieving server with id {id}: {str(e)}")
            raise

    async def get_server_by_client_id(self, cid: str) -> Server | None:
        try:
            result = await self.db.execute(
                select(Server).where(Server.client_id == cid)
            )
            server = result.scalars().first()
            return server
        except SQLAlchemyError as e:
            logger.exception(f"Error retrieving server with client_id {cid}: {str(e)}")
            raise

    async def get_servers(self):
        try:
            result = await self.db.execute(select(Server))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.exception(f"Error retrieving servers: {str(e)}")
            raise

    async def update_server(self, id: int, data: dict) -> Server | None:
        try:
            server = await self.get_server_by_id(id)
            for key, value in data.items():
                setattr(server, key, value)

            await self.db.commit()
            await self.db.refresh(server)
            return server
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Error updating server with id {id}: {str(e)}")
            raise

    async def delete_server(self, id: int) -> bool:
        try:
            server = await self.get_server_by_id(id)
            if not server:
                return False

            await self.db.delete(server)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Error deleting server with id {id}: {str(e)}")
            raise