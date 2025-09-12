from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.postgres import Base
from enums import SURVEY_STEP_TYPE


class SurveyORM(Base):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    survey_steps: Mapped[list["SurveyStepORM"]] = relationship(cascade="all, delete-orphan",
                                                               passive_deletes=True)


class SurveyStepORM(Base):
    __tablename__ = "survey_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    position: Mapped[int]
    text: Mapped[str]
    type: Mapped[SURVEY_STEP_TYPE] = mapped_column(
        PgEnum(SURVEY_STEP_TYPE, name="survey_step_types", create_type=True)
    )
    survey_id: Mapped[int] = mapped_column(
        ForeignKey("surveys.id", ondelete="CASCADE")
    )


class SurveyResultORM(Base):
    __tablename__ = "survey_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    survey: Mapped["SurveyORM"] = relationship()
    survey_step_results: Mapped[list["SurveyStepResultORM"]] = relationship(
        back_populates="survey_result"
    )


class SurveyStepResultORM(Base):
    __tablename__ = "survey_step_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    survey_step_id: Mapped[int] = mapped_column(ForeignKey("survey_steps.id", ondelete="CASCADE"))
    result: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    survey_result_id: Mapped[int] = mapped_column(ForeignKey("survey_results.id", ondelete="CASCADE"))

    survey_step: Mapped["SurveyStepORM"] = relationship()
    survey_result: Mapped["SurveyResultORM"] = relationship(back_populates="survey_step_results")

