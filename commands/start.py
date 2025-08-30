from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_wrapper import AiogramWrapper
from commands.base_command import BaseCommand
from db.service.abc_services import ABCServices
from resources.messages import HELLO_MESSAGE
from states import States

if TYPE_CHECKING:
    from .manager import Manager

class Start(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper):
        super().__init__(manager, db, aiogram_wrapper)

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.aiogram_wrapper.answer_massage(message=message, text=HELLO_MESSAGE)
        await self.aiogram_wrapper.set_state(state, States.MAIN_MENU)
        await self.manager.launch('main_menu', message, state, command)
