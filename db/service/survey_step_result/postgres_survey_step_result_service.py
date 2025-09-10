from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.postgres import SESSION_FACTORY
from db.postgres_models import SurveyStepResultORM
from db.service.survey_step_result.async_survey_step_result_service import AsyncSurveyStepResultService
from dtos import SurveyStepResult
from mappers.survey_step_result_mapper import SurveyStepResultMapper


class PostgresSurveyStepResultService(AsyncSurveyStepResultService):
    async def save_survey_step_result(self, survey_step_result: SurveyStepResult) -> SurveyStepResult:
        async with SESSION_FACTORY() as session:
            added_result = SurveyStepResultMapper.to_entity(survey_step_result)
            session.add(added_result)
            await session.commit()
            await session.refresh(added_result)
            added_result = await session.scalar(select(SurveyStepResultORM)
                                               .where(SurveyStepResultORM.id == added_result.id)
                                               .options(selectinload(SurveyStepResultORM.survey_step),
                                                        selectinload(SurveyStepResultORM.survey_result)))
            return SurveyStepResultMapper.to_dto(added_result)

    async def get_survey_step_result(self, id: int) -> Optional[SurveyStepResult]:
        async with SESSION_FACTORY() as session:
            survey_step_result = await session.scalar(select(SurveyStepResultORM)
                                                    .where(SurveyStepResultORM.id == id)
                                                    .options(selectinload(SurveyStepResultORM.survey_step),
                                                             selectinload(SurveyStepResultORM.survey_result)))
            return SurveyStepResultMapper.to_dto(survey_step_result)

    async def get_survey_step_results_by_survey_result(self, survey_result_id: int) -> List[SurveyStepResult]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyStepResultORM)
                .where(SurveyStepResultORM.survey_result_id == survey_result_id)
                .options(selectinload(SurveyStepResultORM.survey_step),
                         selectinload(SurveyStepResultORM.survey_result))
            )
            survey_step_results = result.all()
            return [SurveyStepResultMapper.to_dto(survey_step_result) for survey_step_result in survey_step_results]

    async def get_survey_step_results_by_step(self, survey_step_id: int) -> List[SurveyStepResult]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyStepResultORM)
                .where(SurveyStepResultORM.survey_step_id == survey_step_id)
                .options(selectinload(SurveyStepResultORM.survey_step),
                         selectinload(SurveyStepResultORM.survey_result))
            )
            survey_step_results = result.all()
            return [SurveyStepResultMapper.to_dto(survey_step_result) for survey_step_result in survey_step_results]

    async def get_all_survey_step_results(self) -> List[SurveyStepResult]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyStepResultORM)
                .options(selectinload(SurveyStepResultORM.survey_step),
                         selectinload(SurveyStepResultORM.survey_result))
            )
            survey_step_results = result.all()
            return [SurveyStepResultMapper.to_dto(survey_step_result) for survey_step_result in survey_step_results]

    async def update_survey_step_result(self, survey_step_result: SurveyStepResult) -> SurveyStepResult:
        async with SESSION_FACTORY() as session:
            updated_result = SurveyStepResultMapper.to_entity(survey_step_result)
            updated_result = await session.merge(updated_result)
            await session.commit()
            await session.refresh(updated_result)
            updated_result = await session.scalar(select(SurveyStepResultORM)
                                                 .where(SurveyStepResultORM.id == updated_result.id)
                                                 .options(selectinload(SurveyStepResultORM.survey_step),
                                                          selectinload(SurveyStepResultORM.survey_result)))
            return SurveyStepResultMapper.to_dto(updated_result)

    async def delete_survey_step_result(self, id: int) -> None:
        async with SESSION_FACTORY() as session:
            survey_step_result = await session.get(SurveyStepResultORM, id)
            await session.delete(survey_step_result)
            await session.commit()
