from db.redis import RedisStorage
from db.service.abc_services import ABCServices
from db.service.survey.async_survey_service import AsyncSurveyService
from db.service.survey.postgres_survey_service import PostgresSurveyService
from db.service.survey.survey_service import SurveyService
from db.service.survey_steps.async_survey_steps_service import AsyncSurveyStepService
from db.service.survey_steps.postgres_survey_steps_service import PostgresSurveyStepService
from db.service.survey_steps.survey_steps_service import SurveyStepService
from db.service.user.async_user_service import AsyncUserService
from db.service.user.redis_user_service import RedisUserService
from db.service.user.user_service import UserService


class Services(ABCServices):
    def __init__(self, redis_client: RedisStorage):
        self.redis_client = redis_client
        self.user_service = RedisUserService(redis_client)
        self.survey_steps_service = PostgresSurveyStepService()
        self.survey_service = PostgresSurveyService()

    @property
    def user(self) -> UserService | AsyncUserService:
        return self.user_service

    @property
    def survey_step(self) -> SurveyStepService | AsyncSurveyStepService:
        return self.survey_steps_service

    @property
    def survey(self) -> SurveyService | AsyncSurveyService:
        return self.survey_service
