from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.postgres import SESSION_FACTORY
from db.postgres_models import SurveyResultORM
from db.service.survey_result.async_survey_result_service import AsyncSurveyResultService
from dtos import SurveyResult
from mappers.survey_result_mapper import SurveyResultMapper


class PostgresSurveyResultService(AsyncSurveyResultService):
    async def save_survey_result(self, survey_result: SurveyResult) -> SurveyResult:
        async with SESSION_FACTORY() as session:
            added_result = SurveyResultMapper.to_entity(survey_result)
            session.add(added_result)
            await session.commit()
            await session.refresh(added_result)
            added_result = await session.scalar(select(SurveyResultORM)
                                               .where(SurveyResultORM.id == added_result.id)
                                               .options(selectinload(SurveyResultORM.survey),
                                                        selectinload(SurveyResultORM.survey_step_results)))
            return SurveyResultMapper.to_dto(added_result)

    async def get_survey_result(self, id: int) -> Optional[SurveyResult]:
        async with SESSION_FACTORY() as session:
            survey_result = await session.scalar(select(SurveyResultORM)
                                                .where(SurveyResultORM.id == id)
                                                .options(selectinload(SurveyResultORM.survey),
                                                         selectinload(SurveyResultORM.survey_step_results)))
            return SurveyResultMapper.to_dto(survey_result)

    async def get_survey_results_by_user(self, user_id: int) -> List[SurveyResult]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyResultORM)
                .where(SurveyResultORM.user_id == user_id)
                .options(selectinload(SurveyResultORM.survey),
                         selectinload(SurveyResultORM.survey_step_results))
            )
            survey_results = result.all()
            return [SurveyResultMapper.to_dto(survey_result) for survey_result in survey_results]

    async def get_all_survey_results(self) -> List[SurveyResult]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyResultORM)
                .options(selectinload(SurveyResultORM.survey),
                         selectinload(SurveyResultORM.survey_step_results))
            )
            survey_results = result.all()
            return [SurveyResultMapper.to_dto(survey_result) for survey_result in survey_results]

    async def update_survey_result(self, survey_result: SurveyResult) -> SurveyResult:
        async with SESSION_FACTORY() as session:
            updated_result = SurveyResultMapper.to_entity(survey_result)
            updated_result = await session.merge(updated_result)
            await session.commit()
            await session.refresh(updated_result)
            updated_result = await session.scalar(select(SurveyResultORM)
                                                 .where(SurveyResultORM.id == updated_result.id)
                                                 .options(selectinload(SurveyResultORM.survey),
                                                          selectinload(SurveyResultORM.survey_step_results)))
            return SurveyResultMapper.to_dto(updated_result)

    async def delete_survey_result(self, id: int) -> None:
        async with SESSION_FACTORY() as session:
            survey_result = await session.get(SurveyResultORM, id)
            await session.delete(survey_result)
            await session.commit()
