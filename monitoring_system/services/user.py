from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils import hash_password, verify_password
from models.user import User
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import select, or_
from core.settings import settings
from datetime import datetime, UTC, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self._db = db

    @property
    def db(self):
        return self._db


    @staticmethod
    def create_jwt_token(user_id: int, role: str):
        expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "exp": expire,
            "sub": str(user_id),
            "role": role
        }

        encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_jwt_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except ExpiredSignatureError:
            logging.info("JWT token has expired")
            raise
        except JWTError as e:
            logging.info(f"Error decoding JWT token: {str(e)}")
            raise

    async def register_user(self, data) -> bool:
        try:
            existing_user = await self.db.execute(
                select(User).where(or_(
                    User.username == data['username'],
                    User.email == data['email']
                    )
                )
            )

            if existing_user.scalars().first():
                raise HTTPException(status_code=400, detail="User with username or email already exists")

            password = data.pop('password')

            new_user = User(**data)
            new_user.hashed_password = hash_password(password)

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logging.exception(f"Error registering user: {str(e)}")
            raise

    async def login_user(self, data):
        try:
            result = await self.db.execute(
                select(User).where(User.username == data['username'])
            )
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")

            if not verify_password(data['password'], user.hashed_password):
                raise HTTPException(status_code=401, detail="Invalid username or password")

            token = UserService.create_jwt_token(user.id, user.role)

            return {"access_token": token, "token_type": "bearer"}
        except SQLAlchemyError as e:
            logging.exception(f"Error logging in user: {str(e)}")
            raise

    async def get_current_user(self, payload):
        try:
            user_id = int(payload["sub"])
            res = await self.db.execute(select(User).where(User.id == user_id))
            user = res.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except SQLAlchemyError as e:
            logger.exception("Unexpected error during retrieving current user")
            raise

    async def change_current_user(self, data, user_id: int):
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            for key, value in data.items():
                if key == "password":
                    setattr(user, "hashed_password", hash_password(value))
                else:
                    setattr(user, key, value)

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Error changing user data for user id {user_id}: {str(e)}")
            raise

    async def delete_current_user(self, payload):
        try:
            user = await self.get_current_user(payload)

            await self.db.delete(user)
            await self.db.commit()

            return True
        except SQLAlchemyError as e:
            logger.exception("Unexpected error during deleting current user")
            raise

    async def get_user_by_id(self, user_id: int):
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            logger.exception(f"Error retrieving user by id {user_id}: {str(e)}")
            raise

    async def get_users(self):
        try:
            result = await self.db.execute(select(User))
            users = result.scalars().all()
            return users
        except SQLAlchemyError as e:
            logger.exception(f"Error retrieving all users: {str(e)}")
            raise

    async def update_user(self ,user_id, data):
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            for key, value in data.items():
                if key == "password":
                    setattr(user, "hashed_password", hash_password(value))
                elif key != "id":
                    setattr(user, key, value)

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Error updating user id {user_id}: {str(e)}")
            raise

    async def delete_user(self, user_id):
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            await self.db.delete(user)
            await self.db.commit()

            return True
        except SQLAlchemyError as e:
            logger.exception(f"Error deleting user id {user_id}: {str(e)}")
            raise