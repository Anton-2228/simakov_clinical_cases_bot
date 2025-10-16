import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory
from db.service.abc_services import ABCServices
from enums import ListUserMainMenuActions
from environments import TARGETED_SURVEY_ID
from keyboards_generators import get_keyboard_for_user_main_menu
from resources.messages import USER_MAIN_MENU_MESSAGE
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class UserMainMenu(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._take_the_survey, UserMainMenuCallbackFactory.filter(F.action == ListUserMainMenuActions.TAKE_THE_SURVEY))
        self.aiogram_wrapper.register_callback(self._send_message_to_admin, UserMainMenuCallbackFactory.filter(F.action == ListUserMainMenuActions.SEND_MESSAGE_TO_ADMIN))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        keyboard_builder = get_keyboard_for_user_main_menu()
        text_message = USER_MAIN_MENU_MESSAGE
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=message,
                                                                         text=text_message,
                                                                         reply_markup=keyboard_builder.as_markup())

    async def _take_the_survey(self, callback: CallbackQuery, callback_data: UserMainMenuCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.TAKE_THE_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.message.chat.id)
        # await self.manager.launch(name="select_take_survey",
        #                           message=callback.message,
        #                           state=state)
        await self.manager.launch(name="take_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=int(TARGETED_SURVEY_ID))
        await callback.answer()

    async def _send_message_to_admin(self, callback: CallbackQuery, callback_data: UserMainMenuCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SEND_MESSAGE_TO_ADMIN)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.message.chat.id)
        await self.manager.launch(name="send_message_to_admin",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
