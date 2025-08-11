from typing import Optional, List

from db.redis import RedisStorage
from db.service.user.async_user_service import AsyncUserService
from enums import USER_TYPE
from models import User


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

    async def get_admins(self) -> List[User]:
        users_id = await self.redis_client.get_list(key="all_users")
        admins = []
        for user_id in users_id:
            user = await self.redis_client.get_value(key=user_id, return_type=User)
            if user.user_type == USER_TYPE.ADMIN:
                admins.append(user)
        return admins
