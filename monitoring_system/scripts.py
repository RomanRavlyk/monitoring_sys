from models.user import User
from schemas.user import UserCreateAdmin
from db.database import get_db
from services.user import UserService


async def create_super_user():
    async for db in get_db():

        user = UserCreateAdmin(
            username="admin",
            password="admin123",
            role="ADMIN",
            email="roman.ravlyk111@gmail.com",
            slack_id="sldlasdlasd",
            is_active=True
        )

        service = UserService(db)

        if await service.register_user(user.model_dump()):
            print("Super user created successfully.")
        else:
            print("Failed to create super user.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_super_user())