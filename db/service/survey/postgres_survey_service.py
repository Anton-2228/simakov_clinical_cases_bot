from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.postgres import SESSION_FACTORY
from db.postgres_models import SurveyORM
from db.service.survey.async_survey_service import AsyncSurveyService
from dtos import Survey
from mappers.survey_mapper import SurveyMapper


class PostgresSurveyService(AsyncSurveyService):
    async def save_survey(self, survey: Survey) -> Survey:
        async with SESSION_FACTORY() as session:
            added_survey = SurveyMapper.to_entity(survey)
            session.add(added_survey)
            await session.commit()
            await session.refresh(added_survey)
            added_survey = await session.scalar(select(SurveyORM)
                                               .where(SurveyORM.id == added_survey.id)
                                               .options(selectinload(SurveyORM.survey_steps)))
            return SurveyMapper.to_dto(added_survey)

    async def get_all_surveys(self) -> List[Survey]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyORM)
                .options(selectinload(SurveyORM.survey_steps))
            )
            surveys = result.all()
            return [SurveyMapper.to_dto(survey) for survey in surveys]

    async def get_survey(self, id: int) -> Optional[Survey]:
        async with SESSION_FACTORY() as session:
            survey = await session.scalar(select(SurveyORM)
                                         .where(SurveyORM.id == id)
                                         .options(selectinload(SurveyORM.survey_steps)))
            return SurveyMapper.to_dto(survey)

    async def update_survey(self, survey: Survey) -> Survey:
        async with SESSION_FACTORY() as session:
            updated_survey = SurveyMapper.to_entity(survey)
            updated_survey = await session.merge(updated_survey)
            await session.commit()
            await session.refresh(updated_survey)
            updated_survey = await session.scalar(select(SurveyORM)
                                                 .where(SurveyORM.id == updated_survey.id)
                                                 .options(selectinload(SurveyORM.survey_steps)))
            return SurveyMapper.to_dto(updated_survey)

    async def delete_survey(self, id: int) -> None:
        async with SESSION_FACTORY() as session:
            survey = await session.get(SurveyORM, id)
            await session.delete(survey)
            await session.commit()
