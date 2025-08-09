from db.redis import RedisStorage
from db.service.services import Services
from db.service.user.async_user_service import AsyncUserService
from db.service.user.redis_user_service import RedisUserService
from db.service.user.user_service import UserService


class RedisServices(Services):
    def __init__(self, redis_client: RedisStorage):
        self.redis_client = redis_client
        self.user_service = RedisUserService(redis_client)

    @property
    def user(self) -> UserService | AsyncUserService:
        return self.user_service
