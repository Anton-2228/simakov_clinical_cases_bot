import uuid
from typing import Optional

from db.redis import RedisStorage
from db.service.user.async_user_service import AsyncUserService
from models import User
from utils import get_uuid


class RedisUserService(AsyncUserService):
    def __init__(self, redis_client: RedisStorage):
        self.redis_client = redis_client

    async def save_user(self, user: User) -> str:
        all_users = await self.redis_client.get_list(key="all_users")
        if all_users:
            all_users.append(user.telegram_id)
        else:
            all_users = [user.telegram_id]
        await self.redis_client.set_value(key="all_users", value=all_users)
        await self.redis_client.set_value(key=str(user.telegram_id), value=user)
        return str(user.telegram_id)

    async def get_user(self, telegram_id: str) -> Optional[User]:
        user = await self.redis_client.get_value(key=telegram_id, return_type=User)
        return user
