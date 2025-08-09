from abc import ABC, abstractmethod
from typing import Optional

from models import User


class UserService(ABC):
    @abstractmethod
    def save_user(self, user: User) -> str:
        """
        Метод сохраняет пользователя в базу данных

        :param user - объект пользователя

        :return:
            uuid сохраненного пользователя
        """
        pass

    @abstractmethod
    def get_user(self, telegram_id: str) -> Optional[User]:
        """
        Метод получает пользователя из базы данных

        :param telegram_id - строка с telegram_id пользователя

        :return:
            объект пользователя с метаинформацией
        """
        pass