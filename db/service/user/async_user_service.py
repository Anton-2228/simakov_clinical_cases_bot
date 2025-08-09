from abc import ABC, abstractmethod
from typing import Optional

from models import User


class AsyncUserService(ABC):
    @abstractmethod
    async def save_user(self, user: User) -> str:
        """
        Метод асинхронно сохраняет пользователя в базу данных

        :return:
            uuid сохраненного пользователя
        """
        pass

    @abstractmethod
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """
        Метод асинхронно получает пользователя из базы данных

        :return:
            объект пользователя с метаинформацией
        """
        pass