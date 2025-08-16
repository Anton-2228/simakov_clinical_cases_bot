from db.postgres import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy import ForeignKey

from enums import SURVEY_STEP_TYPE

from typing import TYPE_CHECKING


class SurveyORM(Base):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    survey_steps: Mapped[list["SurveyStepORM"]] = relationship(back_populates="survey")


class SurveyStepORM(Base):
    __tablename__ = "survey_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    position: Mapped[int]
    type: Mapped[SURVEY_STEP_TYPE] = mapped_column(
        PgEnum(SURVEY_STEP_TYPE, name="survey_step_types", create_type=True)
    )
    survey_id: Mapped[int] = mapped_column(
        ForeignKey("surveys.id", ondelete="CASCADE")
    )

    survey: Mapped["SurveyORM"] = relationship(back_populates="survey_steps")
