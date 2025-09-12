from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from enums import SURVEY_STEP_TYPE
from db.postgres_models import MessageStatus, MESSAGE_TYPE


class Survey(BaseModel):
    id: Optional[int] = None
    name: str
    start_message: str
    finish_message: str
    survey_steps: Optional[list["SurveyStep"]] = None


class SurveyStep(BaseModel):
    id: Optional[int] = None
    survey_id: int
    name: str
    position: int
    text: str
    type: SURVEY_STEP_TYPE


class SurveyResult(BaseModel):
    id: Optional[int] = None
    user_id: int
    survey_id: int
    created_at: Optional[datetime] = None
    survey: Optional[Survey] = None
    survey_step_results: Optional[list["SurveyStepResult"]] = None


class SurveyStepResult(BaseModel):
    id: Optional[int] = None
    survey_step_id: int
    result: str
    survey_result_id: int
    created_at: Optional[datetime] = None


class Message(BaseModel):
    id: Optional[int] = None
    text: str
    from_user_id: int
    to_user_id: Optional[int] = None
    status: MessageStatus
    type: MESSAGE_TYPE
