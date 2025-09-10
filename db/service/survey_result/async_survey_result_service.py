from abc import ABC, abstractmethod
from typing import List, Optional

from dtos import SurveyResult


class AsyncSurveyResultService(ABC):
    @abstractmethod
    async def save_survey_result(self, survey_result: SurveyResult) -> SurveyResult:
        """
        Метод сохраняет результат опроса в базу данных

        :param survey_result - объект результата опроса

        :return:
            объект сохраненного результата опроса
        """

    @abstractmethod
    async def get_survey_result(self, id: int) -> Optional[SurveyResult]:
        """
        Метод получает результат опроса из базы данных

        :param id - id результата опроса

        :return:
            объект результата опроса
        """

    @abstractmethod
    async def get_survey_results_by_user(self, user_id: int) -> List[SurveyResult]:
        """
        Метод получает все результаты опросов пользователя из базы данных

        :param user_id - id пользователя

        :return:
            список всех результатов опросов пользователя
        """

    @abstractmethod
    async def get_all_survey_results(self) -> List[SurveyResult]:
        """
        Метод получает все результаты опросов из базы данных

        :return:
            список всех результатов опросов
        """

    @abstractmethod
    async def update_survey_result(self, survey_result: SurveyResult) -> SurveyResult:
        """
        Метод обновляет результат опроса в базе данных

        :param survey_result - объект результата опроса

        :return:
            объект результата опроса
        """

    @abstractmethod
    async def delete_survey_result(self, id: int) -> None:
        """
        Метод удаляет указанный результат опроса
        :param id: id результата опроса, который надо удалить
        :return:
        """
