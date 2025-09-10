from abc import ABC, abstractmethod

from db.minio.minio import AsyncMinioClient
from db.service.survey.async_survey_service import AsyncSurveyService
from db.service.survey.survey_service import SurveyService
from db.service.survey_result.async_survey_result_service import AsyncSurveyResultService
from db.service.survey_result.survey_result_service import SurveyResultService
from db.service.survey_step_result.async_survey_step_result_service import AsyncSurveyStepResultService
from db.service.survey_step_result.survey_step_result_service import SurveyStepResultService
from db.service.survey_steps.async_survey_steps_service import \
    AsyncSurveyStepService
from db.service.survey_steps.survey_steps_service import SurveyStepService
from db.service.user.async_user_service import AsyncUserService
from db.service.user.user_service import UserService


class ABCServices(ABC):
    @property
    @abstractmethod
    def user(self) -> UserService | AsyncUserService:
        pass

    @property
    @abstractmethod
    def survey_step(self) -> SurveyStepService | AsyncSurveyStepService:
        pass

    @property
    @abstractmethod
    def survey(self) -> SurveyService | AsyncSurveyService:
        pass

    @property
    @abstractmethod
    def survey_result(self) -> SurveyResultService | AsyncSurveyResultService:
        pass

    @property
    @abstractmethod
    def survey_step_result(self) -> SurveyStepResultService | AsyncSurveyStepResultService:
        pass

    @property
    @abstractmethod
    def files_storage(self) -> AsyncMinioClient:
        pass
