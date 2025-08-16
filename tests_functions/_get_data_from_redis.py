import asyncio
from typing import Type, TypeVar

from db.redis import RedisStorage
from db.service.services import Services
from enums import USER_TYPE
from models import User

T = TypeVar("T")

async def main(db: Services, key: str, type: Type[T]):
    data = await db.redis_client.get_value(key=key, return_type=type)
    print(data)

if __name__ == "__main__":
    REDIS = RedisStorage(host="127.0.0.1", port=6379)
    DB = Services(redis_client=REDIS)
    asyncio.run(main(db=DB, key="173202775", type=User))
