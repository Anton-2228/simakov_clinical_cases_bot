from typing import Optional, List

from sqlalchemy import select, update

from db.postgres import SESSION_FACTORY
from db.postgres_models import SurveyStepORM, SurveyORM
from db.redis import RedisStorage
from db.service.survey.async_survey_service import AsyncSurveyService
from db.service.survey_steps.async_survey_steps_service import AsyncSurveyStepService
from db.service.user.async_user_service import AsyncUserService
from dtos import Survey
from enums import USER_TYPE
from mappers.survey_mapper import SurveyMapper
from models import User


class PostgresSurveyService(AsyncSurveyService):
    async def save_survey(self, survey: Survey) -> Survey:
        async with SESSION_FACTORY() as session:
            added_survey = SurveyMapper.to_entity(survey)
            session.add(added_survey)
            await session.commit()
            await session.refresh(added_survey)
            return SurveyMapper.to_dto(added_survey)

    async def get_survey(self, id: int) -> Optional[Survey]:
        async with SESSION_FACTORY() as session:
            survey = await session.get(SurveyORM, id)
            return SurveyMapper.to_dto(survey)

    async def update_survey(self, survey: Survey) -> Survey:
        async with SESSION_FACTORY() as session:
            updated_survey = SurveyMapper.to_entity(survey)
            updated_survey = await session.merge(updated_survey)
            await session.commit()
            await session.refresh(updated_survey)
            return SurveyMapper.to_dto(updated_survey)
