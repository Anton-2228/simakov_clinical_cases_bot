import pickle
from typing import Optional, Type, TypeVar, Any

from redis.asyncio import Redis

from environments import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

T = TypeVar("T")

class RedisStorage:
    def __init__(self, host: str, port: int):
        self.redis = Redis(host=host, port=int(port), db=0, password=REDIS_PASSWORD)

    async def _get(self, key: str, return_type: Type[T]) -> Optional[T]:
        raw_data: Optional[bytes] = await self.redis.get(key)
        if raw_data is None:
            return None
        data = pickle.loads(raw_data)
        assert isinstance(data, return_type)
        return data

    async def get_str(self, key: str) -> Optional[str]:
        return await self._get(key=key, return_type=str)

    async def get_dict(self, key: str) -> Optional[dict]:
        return await self._get(key=key, return_type=dict)

    async def get_list(self, key: str) -> Optional[list]:
        return await self._get(key=key, return_type=list)

    async def get_value(self, key: str, return_type: Type[T]) -> Optional[T]:
        return await self._get(key=key, return_type=return_type)

    async def set_value(self, key: str, value: Any) -> None:
        await self.redis.set(name=key, value=pickle.dumps(value))

    async def delete_value(self, key: str) -> None:
        await self.redis.delete(key)
