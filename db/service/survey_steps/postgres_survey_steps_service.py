from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from db.postgres import SESSION_FACTORY
from db.postgres_models import SurveyStepORM
from db.redis import RedisStorage
from db.service.survey_steps.async_survey_steps_service import AsyncSurveyStepService
from db.service.user.async_user_service import AsyncUserService
from dtos import SurveyStep, Survey
from enums import USER_TYPE
from mappers.survey_mapper import SurveyMapper
from mappers.survey_step_mapper import SurveyStepMapper
from models import User


class PostgresSurveyStepService(AsyncSurveyStepService):
    async def save_survey_step(self, survey_step: SurveyStep) -> SurveyStep:
        async with SESSION_FACTORY() as session:
            added_step = SurveyStepMapper.to_entity(survey_step)
            session.add(added_step)
            await session.commit()
            await session.refresh(added_step)
            added_step = await session.scalar(select(SurveyStepORM)
                                              .where(SurveyStepORM.id == added_step.id)
                                              .options(selectinload(SurveyStepORM.survey)))
            return SurveyStepMapper.to_dto(added_step)

    async def get_survey_step(self, id: int) -> Optional[SurveyStep]:
        async with SESSION_FACTORY() as session:
            # survey_step = await session.get(SurveyStepORM, id)
            survey_step = await session.scalar(select(SurveyStepORM)
                                               .where(SurveyStepORM.id == id)
                                               .options(selectinload(SurveyStepORM.survey)))
            return SurveyStepMapper.to_dto(survey_step)

    async def get_all_survey_steps(self, survey_id: int) -> List[SurveyStep]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyStepORM)
                .where(SurveyStepORM.survey_id == survey_id)
                .options(selectinload(SurveyStepORM.survey))
            )
            survey_steps = result.all()
            return [SurveyStepMapper.to_dto(survey_step) for survey_step in survey_steps]

    async def update_survey_step(self, survey_step: SurveyStep) -> SurveyStep:
        async with SESSION_FACTORY() as session:
            updated_step = SurveyStepMapper.to_entity(survey_step)
            updated_step = await session.merge(updated_step)
            await session.commit()
            await session.refresh(updated_step)
            updated_step = await session.scalar(select(SurveyStepORM)
                                                .where(SurveyStepORM.id == updated_step.id)
                                                .options(selectinload(SurveyStepORM.survey)))
            return SurveyStepMapper.to_dto(updated_step)

    async def delete_step(self, id: int) -> None:
        async with SESSION_FACTORY() as session:
            step = await session.get(SurveyStepORM, id)
            await session.delete(step)
            await session.commit()
