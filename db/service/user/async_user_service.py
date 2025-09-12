from abc import ABC, abstractmethod
from typing import List, Optional

from enums import USER_TYPE
from models import User


class AsyncUserService(ABC):
    @abstractmethod
    async def save_user(self, user: User) -> str:
        """
        Метод асинхронно сохраняет пользователя в базу данных

        :return:
            uuid сохраненного пользователя
        """

    @abstractmethod
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """
        Метод асинхронно получает пользователя из базы данных

        :return:
            объект пользователя с метаинформацией
        """

    async def get_users_by_type(self, user_type: USER_TYPE) -> List[User]:
        """
        Метод для получения всех пользователей определенного типа
        :param user_type: тип, пользователей которого будет возвращен
        :return: список пользователей
        """

    async def get_users(self) -> List[User]:
        """
        Метод для получения всех пользователей
        :return: список пользователей
        """

    async def update_user(self, user: User) -> None:
        """
        Метод для обновления информации о пользователе. Значение будет обновлено только если пользователь есть в базе
        :param user: объект пользователя
        :return:
        """
