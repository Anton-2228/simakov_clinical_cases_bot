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
        await self.redis_client.set_value(key=str(user.telegram_id), value=user)
        return str(user.telegram_id)

    async def get_user(self, telegram_id: str) -> Optional[User]:
        user = await self.redis_client.get_value(key=telegram_id, return_type=User)
        return user
