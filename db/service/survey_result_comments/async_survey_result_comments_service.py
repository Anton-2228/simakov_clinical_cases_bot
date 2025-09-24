from abc import ABC, abstractmethod
from typing import List, Optional

from dtos import SurveyResultComments


class AsyncSurveyResultCommentsService(ABC):
    @abstractmethod
    async def save_survey_result_comment(self, survey_result_comment: SurveyResultComments) -> SurveyResultComments:
        """
        Метод сохраняет комментарий к результату опроса в базу данных

        :param survey_result_comment - объект комментария к результату опроса

        :return:
            объект сохраненного комментария к результату опроса
        """

    @abstractmethod
    async def get_survey_result_comment(self, id: int) -> Optional[SurveyResultComments]:
        """
        Метод получает комментарий к результату опроса из базы данных

        :param id - id комментария к результату опроса

        :return:
            объект комментария к результату опроса
        """

    @abstractmethod
    async def get_survey_result_comments_by_survey_result(self, survey_result_id: int) -> List[SurveyResultComments]:
        """
        Метод получает все комментарии к конкретному результату опроса из базы данных

        :param survey_result_id - id результата опроса

        :return:
            список всех комментариев к результату опроса
        """

    @abstractmethod
    async def get_all_survey_result_comments(self) -> List[SurveyResultComments]:
        """
        Метод получает все комментарии к результатам опросов из базы данных

        :return:
            список всех комментариев к результатам опросов
        """

    @abstractmethod
    async def update_survey_result_comment(self, survey_result_comment: SurveyResultComments) -> SurveyResultComments:
        """
        Метод обновляет комментарий к результату опроса в базе данных

        :param survey_result_comment - объект комментария к результату опроса

        :return:
            объект комментария к результату опроса
        """

    @abstractmethod
    async def delete_survey_result_comment(self, id: int) -> None:
        """
        Метод удаляет указанный комментарий к результату опроса
        :param id: id комментария к результату опроса, который надо удалить
        :return:
        """
