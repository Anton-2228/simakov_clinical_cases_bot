from abc import ABC, abstractmethod
from typing import List, Optional

from dtos import Message


class MessageService(ABC):
    @abstractmethod
    def save_message(self, message: Message) -> Message:
        """
        Метод сохраняет сообщение в базу данных

        :param message - объект сообщения

        :return:
            объект сохраненного сообщения
        """

    @abstractmethod
    def get_all_messages(self) -> List[Message]:
        """
        Метод получает все сообщения из базы данных

        :return:
            Список объектов сообщений
        """

    @abstractmethod
    def get_message(self, id: int) -> Optional[Message]:
        """
        Метод получает сообщение из базы данных

        :param id - id сообщения

        :return:
            объект сообщения
        """

    @abstractmethod
    def update_message(self, message: Message) -> Message:
        """
        Метод обновляет сообщение в базе данных

        :param message - объект сообщения

        :return:
            объект сообщения
        """

    @abstractmethod
    def delete_message(self, id: int) -> None:
        """
        Метод удаляет указанное сообщение
        :param id: id сообщения, которое надо удалить
        :return:
        """

    @abstractmethod
    def get_messages_by_user(self, user_id: int) -> List[Message]:
        """
        Метод получает все сообщения для указанного пользователя

        :param user_id - id пользователя

        :return:
            Список объектов сообщений
        """

    @abstractmethod
    def get_messages_by_status(self, status: "MessageStatus") -> List[Message]:
        """
        Метод получает все сообщения с указанным статусом

        :param status - статус сообщения

        :return:
            Список объектов сообщений
        """

    @abstractmethod
    def get_messages_by_type(self, message_type: "MESSAGE_TYPE") -> List[Message]:
        """
        Метод получает все сообщения с указанным типом

        :param message_type - тип сообщения

        :return:
            Список объектов сообщений
        """

    @abstractmethod
    def get_messages_by_type_and_status(self, message_type: "MESSAGE_TYPE", status: "MessageStatus") -> List[Message]:
        """
        Метод получает все сообщения с указанным типом и статусом

        :param message_type - тип сообщения
        :param status - статус сообщения

        :return:
            Список объектов сообщений
        """