from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.postgres import SESSION_FACTORY
from db.postgres_models import SurveyResultCommentsORM
from db.service.survey_result_comments.async_survey_result_comments_service import AsyncSurveyResultCommentsService
from dtos import SurveyResultComments
from mappers.survey_result_comments_mapper import SurveyResultCommentsMapper


class PostgresSurveyResultCommentsService(AsyncSurveyResultCommentsService):
    async def save_survey_result_comment(self, survey_result_comment: SurveyResultComments) -> SurveyResultComments:
        async with SESSION_FACTORY() as session:
            added_comment = SurveyResultCommentsMapper.to_entity(survey_result_comment)
            session.add(added_comment)
            await session.commit()
            await session.refresh(added_comment)
            added_comment = await session.scalar(select(SurveyResultCommentsORM)
                                                .where(SurveyResultCommentsORM.id == added_comment.id))
            return SurveyResultCommentsMapper.to_dto(added_comment)

    async def get_survey_result_comment(self, id: int) -> Optional[SurveyResultComments]:
        async with SESSION_FACTORY() as session:
            comment = await session.scalar(select(SurveyResultCommentsORM)
                                         .where(SurveyResultCommentsORM.id == id))
            return SurveyResultCommentsMapper.to_dto(comment) if comment else None

    async def get_survey_result_comments_by_survey_result(self, survey_result_id: int) -> List[SurveyResultComments]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(
                select(SurveyResultCommentsORM)
                .where(SurveyResultCommentsORM.survey_result_id == survey_result_id)
            )
            comments = result.all()
            return [SurveyResultCommentsMapper.to_dto(comment) for comment in comments]

    async def get_all_survey_result_comments(self) -> List[SurveyResultComments]:
        async with SESSION_FACTORY() as session:
            result = await session.scalars(select(SurveyResultCommentsORM))
            comments = result.all()
            return [SurveyResultCommentsMapper.to_dto(comment) for comment in comments]

    async def update_survey_result_comment(self, survey_result_comment: SurveyResultComments) -> SurveyResultComments:
        async with SESSION_FACTORY() as session:
            updated_comment = SurveyResultCommentsMapper.to_entity(survey_result_comment)
            updated_comment = await session.merge(updated_comment)
            await session.commit()
            await session.refresh(updated_comment)
            updated_comment = await session.scalar(select(SurveyResultCommentsORM)
                                                  .where(SurveyResultCommentsORM.id == updated_comment.id))
            return SurveyResultCommentsMapper.to_dto(updated_comment)

    async def delete_survey_result_comment(self, id: int) -> None:
        async with SESSION_FACTORY() as session:
            comment = await session.get(SurveyResultCommentsORM, id)
            await session.delete(comment)
            await session.commit()
