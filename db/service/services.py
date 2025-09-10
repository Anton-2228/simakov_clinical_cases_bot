from db.minio.minio import AsyncMinioClient
from db.redis import RedisStorage
from db.service.abc_services import ABCServices
from db.service.survey.async_survey_service import AsyncSurveyService
from db.service.survey.postgres_survey_service import PostgresSurveyService
from db.service.survey.survey_service import SurveyService
from db.service.survey_result.async_survey_result_service import AsyncSurveyResultService
from db.service.survey_result.postgres_survey_result_service import PostgresSurveyResultService
from db.service.survey_result.survey_result_service import SurveyResultService
from db.service.survey_step_result.async_survey_step_result_service import AsyncSurveyStepResultService
from db.service.survey_step_result.postgres_survey_step_result_service import PostgresSurveyStepResultService
from db.service.survey_step_result.survey_step_result_service import SurveyStepResultService
from db.service.survey_steps.async_survey_steps_service import \
    AsyncSurveyStepService
from db.service.survey_steps.postgres_survey_steps_service import \
    PostgresSurveyStepService
from db.service.survey_steps.survey_steps_service import SurveyStepService
from db.service.user.async_user_service import AsyncUserService
from db.service.user.redis_user_service import RedisUserService
from db.service.user.user_service import UserService


class Services(ABCServices):
    def __init__(self, redis_client: RedisStorage, minio_client: AsyncMinioClient):
        self.redis_client = redis_client
        self.minio_client = minio_client
        self.user_service = RedisUserService(redis_client)
        self.survey_steps_service = PostgresSurveyStepService()
        self.survey_service = PostgresSurveyService()
        self.survey_result_service = PostgresSurveyResultService()
        self.survey_step_result_service = PostgresSurveyStepResultService()

    @property
    def user(self) -> UserService | AsyncUserService:
        return self.user_service

    @property
    def survey_step(self) -> SurveyStepService | AsyncSurveyStepService:
        return self.survey_steps_service

    @property
    def survey(self) -> SurveyService | AsyncSurveyService:
        return self.survey_service

    @property
    def survey_result(self) -> SurveyResultService | AsyncSurveyResultService:
        return self.survey_result_service

    @property
    def survey_step_result(self) -> SurveyStepResultService | AsyncSurveyStepResultService:
        return self.survey_step_result_service

    @property
    def files_storage(self) -> AsyncMinioClient:
        return self.minio_client
