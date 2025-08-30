from abc import ABC, abstractmethod
from typing import List, Optional

from dtos import Survey


class SurveyService(ABC):
    @abstractmethod
    def save_survey(self, survey: Survey) -> Survey:
        """
        Метод сохраняет опрос в базу данных

        :param survey_step - объект опроса

        :return:
            id сохраненного опроса
        """

    @abstractmethod
    def get_all_surveys(self) -> List[Survey]:
        """
        Метод получает все опросы из базы данных

        :return:
            Список объектов опросов
        """

    @abstractmethod
    def get_survey(self, id: int) -> Optional[Survey]:
        """
        Метод получает опрос из базы данных

        :param id - id опроса

        :return:
            объект опроса
        """


    @abstractmethod
    def update_survey(self, survey: Survey) -> Survey:
        """
        Метод обновляет опрос в базе данных

        :param survey - объект опроса

        :return:
            объект опроса
        """

    @abstractmethod
    def delete_survey(self, id: int) -> None:
        """
        Метод удаляет указанный опрос
        :param id: id опроса, который надо удалить
        :return:
        """
