from abc import ABC, abstractmethod
from typing import List, Optional

from dtos import SurveyStepResult


class SurveyStepResultService(ABC):
    @abstractmethod
    def save_survey_step_result(self, survey_step_result: SurveyStepResult) -> SurveyStepResult:
        """
        Метод сохраняет результат шага опроса в базу данных

        :param survey_step_result - объект результата шага опроса

        :return:
            объект сохраненного результата шага опроса
        """

    @abstractmethod
    def get_survey_step_result(self, id: int) -> Optional[SurveyStepResult]:
        """
        Метод получает результат шага опроса из базы данных

        :param id - id результата шага опроса

        :return:
            объект результата шага опроса
        """

    @abstractmethod
    def get_survey_step_results_by_survey_result(self, survey_result_id: int) -> List[SurveyStepResult]:
        """
        Метод получает все результаты шагов опроса по результату опроса из базы данных

        :param survey_result_id - id результата опроса

        :return:
            список всех результатов шагов опроса
        """

    @abstractmethod
    def get_survey_step_results_by_step(self, survey_step_id: int) -> List[SurveyStepResult]:
        """
        Метод получает все результаты шага опроса из базы данных

        :param survey_step_id - id шага опроса

        :return:
            список всех результатов шага опроса
        """

    @abstractmethod
    def get_all_survey_step_results(self) -> List[SurveyStepResult]:
        """
        Метод получает все результаты шагов опросов из базы данных

        :return:
            список всех результатов шагов опросов
        """

    @abstractmethod
    def update_survey_step_result(self, survey_step_result: SurveyStepResult) -> SurveyStepResult:
        """
        Метод обновляет результат шага опроса в базе данных

        :param survey_step_result - объект результата шага опроса

        :return:
            объект результата шага опроса
        """

    @abstractmethod
    def delete_survey_step_result(self, id: int) -> None:
        """
        Метод удаляет указанный результат шага опроса
        :param id: id результата шага опроса, который надо удалить
        :return:
        """
