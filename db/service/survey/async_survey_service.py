from abc import ABC, abstractmethod
from typing import Optional, List

from dtos import Survey
from enums import USER_TYPE
from models import User


class AsyncSurveyService(ABC):
    @abstractmethod
    async def save_survey(self, survey: Survey) -> Survey:
        """
        Метод сохраняет опрос в базу данных

        :param survey_step - объект опроса

        :return:
            id сохраненного опроса
        """
        pass

    @abstractmethod
    async def get_all_surveys(self) -> List[Survey]:
        """
        Метод получает все опросы из базы данных

        :return:
            Список объектов опросов
        """
        pass

    @abstractmethod
    async def get_survey(self, id: int) -> Optional[Survey]:
        """
        Метод получает опрос из базы данных

        :param id - id опроса

        :return:
            объект опроса
        """
        pass


    @abstractmethod
    async def update_survey(self, survey: Survey) -> Survey:
        """
        Метод обновляет опрос в базе данных

        :param survey - объект опроса

        :return:
            объект опроса
        """
        pass
