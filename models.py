from pydantic import BaseModel

from enums import USER_TYPE


class User(BaseModel):
    telegram_id: int
    full_name: str
    user_type: USER_TYPE
