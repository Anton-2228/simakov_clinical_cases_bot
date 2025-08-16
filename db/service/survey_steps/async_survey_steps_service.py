from abc import ABC, abstractmethod
from typing import Optional, List

from dtos import SurveyStep
from enums import USER_TYPE
from models import User


class AsyncSurveyStepService(ABC):
    @abstractmethod
    async def save_survey_step(self, survey_step: SurveyStep) -> SurveyStep:
        """
        Метод сохраняет шаг опроса в базу данных

        :param survey_step - объект шага опроса

        :return:
            id сохраненного шага
        """
        pass

    @abstractmethod
    async def get_survey_step(self, id: int) -> Optional[SurveyStep]:
        """
        Метод получает шаг опроса из базы данных

        :param id - id шага

        :return:
            объект шага с метаинформацией
        """
        pass

    @abstractmethod
    async def get_all_survey_steps(self, survey_id: int) -> List[SurveyStep]:
        """
        Метод получает все шаги опроса из базы данных

        :param survey_id - id опроса

        :return:
            список всех объектов шагов с метаинформацией
        """
        pass

    @abstractmethod
    async def update_survey_step(self, survey_step: SurveyStep) -> SurveyStep:
        """
        Метод обновляет шаг опроса в базе данных

        :param survey_step - объект шага опроса

        :return:
            объект шага опроса
        """
        pass
