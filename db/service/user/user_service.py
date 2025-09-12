from abc import ABC, abstractmethod
from typing import List, Optional

from enums import USER_TYPE
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

    @abstractmethod
    def get_user(self, telegram_id: str) -> Optional[User]:
        """
        Метод получает пользователя из базы данных

        :param telegram_id - строка с telegram_id пользователя

        :return:
            объект пользователя с метаинформацией
        """

    def get_users_by_type(self, user_type: USER_TYPE) -> List[User]:
        """
        Метод для получения всех пользователей определенного типа
        :param user_type: тип, пользователей которого будет возвращен
        :return: список пользователей
        """

    def get_users(self) -> List[User]:
        """
        Метод для получения всех пользователей
        :return: список пользователей
        """

    def update_user(self, user: User) -> None:
        """
        Метод для обновления информации о пользователе. Значение будет обновлено только если пользователь есть в базе
        :param user: объект пользователя
        :return:
        """
