import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory

from db.service.abc_services import ABCServices
from enums import ListUserMainMenuActions, USER_TYPE
from keyboards_generators import get_keyboard_for_user_main_menu
from models import User
from resources.messages import USER_MAIN_MENU_MESSAGE, REGISTRATION_MESSAGE, REGISTRATION_NOT_VALID_FULL_NAME_MESSAGE
from states import States
from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class Registration(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_full_name, States.REGISTRATION)

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.aiogram_wrapper.set_state(state_context=state, state=States.REGISTRATION)
        text_message = REGISTRATION_MESSAGE
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text_message)

    async def _enter_full_name(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        row_full_name = message.text
        if len(row_full_name.split()) < 2:
            await self.aiogram_wrapper.answer_massage(message=message,
                                                      text=REGISTRATION_NOT_VALID_FULL_NAME_MESSAGE)
            return

        full_name = " ".join(row_full_name.split())
        user = User(telegram_id=message.from_user.id,
                    full_name=full_name,
                    user_type=USER_TYPE.CLIENT)
        await self.db.user.save_user(user=user)
        await self.aiogram_wrapper.clear_state(state_context=state)
        await self.manager.launch(name="start", message=message, state=state, command=command)
