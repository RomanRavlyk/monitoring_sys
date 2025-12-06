import asyncio
import hashlib
import random
import string
import sys

from sqlalchemy.exc import SQLAlchemyError

from exceptions.api_key import ApiKeyDatabaseError, ApiKeyAlreadyExists, ApiKeyNotFound
from schemas.api_key import APIKeySchema
from models.api_key import APIKey

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import async_session

import logging


logger = logging.getLogger(__name__)

class APIKeyService:

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @property
    def db(self):
        return self._db

    @staticmethod
    def generate_random_string():
        length = 128

        characters = string.ascii_letters + string.digits + string.punctuation
        random_str = "".join(random.choice(characters) for _ in range(length))

        return random_str

    @staticmethod
    def generate_hashed_api_key(raw_key: str):

        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        return hashed_key

    async def add_api_key_to_db(self, api_key: str):
        try:
            try:
                await self.get_api_key_by_key(api_key)
                raise ApiKeyAlreadyExists()
            except ApiKeyNotFound:
                pass

            key = APIKey(key=api_key)

            self.db.add(key)
            await self.db.commit()
            await self.db.refresh(key)
            return True

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ApiKeyDatabaseError() from e

    async def get_api_key_by_key(self, api_key: str):

        try:
            result = await self.db.execute(select(APIKey).where(APIKey.key == api_key))
            api_key = result.scalars().first()

            if not api_key:
                raise ApiKeyNotFound()
            return api_key

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ApiKeyDatabaseError() from e

    async def get_api_keys(self):
        try:
            result = await self.db.execute(select(APIKey))
            return [APIKeySchema.model_validate(data).model_dump() for data in result.scalars().all()]
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ApiKeyDatabaseError() from e

    async def delete_api_key(self, key_id: int):
        try:
            key = await self.db.execute(select(APIKey).where(APIKey.id == key_id))
            if not key.scalars().first():
                raise ApiKeyNotFound()

            await self.db.delete(key)
            await self.db.commit()

            return True

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise ApiKeyDatabaseError() from e

async def main():
    async with async_session as session:
        if len(sys.argv) < 2:
            print("Please provide 'add', 'delete' or 'keys' as an argument.")
            sys.exit(1)

        service = APIKeyService(session)
        key = service.generate_hashed_api_key(service.generate_random_string())

        command = sys.argv[1]

        if command == "add":
            await service.add_api_key_to_db(key)

        if command == "delete":
            if len(sys.argv) < 3:
                print("Please provide the key ID to delete.")
                sys.exit(1)
            key_id = int(sys.argv[2])

            await service.delete_api_key(key_id)

        if command == "keys":

            keys = await service.get_api_keys()
            for key in keys:
                print(key)


if __name__ == "__main__":
    asyncio.run(main())

