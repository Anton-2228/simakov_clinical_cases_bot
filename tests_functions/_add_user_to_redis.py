import asyncio

from db.redis import RedisStorage
from db.service.services import Services
from enums import USER_TYPE
from models import User


async def main(db: Services, telegram_id: int, full_name: str, role: USER_TYPE):
    user = User(telegram_id=telegram_id,
                full_name=full_name,
                user_type=role)
    await db.user.save_user(user)

if __name__ == "__main__":
    REDIS = RedisStorage(host="127.0.0.1", port=6379)
    DB = Services(redis_client=REDIS)
    asyncio.run(main(db=DB,
                     telegram_id=173202775,
                     full_name="Зинченко Антон Андреевич",
                     role=USER_TYPE.ADMIN))
