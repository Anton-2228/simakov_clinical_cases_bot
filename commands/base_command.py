from typing import TYPE_CHECKING, Optional

from aiogram import Router, Bot
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_wrapper import AiogramWrapper

from db.service.abc_services import ABCServices

if TYPE_CHECKING:
    from commands import Manager


class BaseCommand:
    def __init__(self,
                 manager: "Manager",
                 db: ABCServices,
                 aiogram_wrapper: AiogramWrapper) -> None:
        self.manager = manager
        self.db = db
        self.aiogram_wrapper = aiogram_wrapper

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject], **kwargs):
        pass
