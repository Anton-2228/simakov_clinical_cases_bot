from abc import ABC, abstractmethod

from db.service.survey.async_survey_service import AsyncSurveyService
from db.service.survey.survey_service import SurveyService
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
