import json
import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AdminMainMenuCallbackFactory
from db.service.abc_services import ABCServices
from enums import ListAdminMainMenuActions
from environments import TARGETED_SURVEY_ID
from keyboards_generators import get_keyboard_for_admin_main_menu
from resources.messages import ADMIN_MAIN_MENU_MESSAGE
from states import States
from utils import get_tmp_path
from xlsx_handler import XLSXHandler

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class AdminMainMenu(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.xlsx_handler = XLSXHandler()
        self.aiogram_wrapper.register_callback(self._take_the_survey, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.TAKE_THE_SURVEY))
        self.aiogram_wrapper.register_callback(self._edit_surveys, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.EDIT_SURVEYS))
        self.aiogram_wrapper.register_callback(self._edit_admin_list, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.EDIT_ADMIN_LIST))
        self.aiogram_wrapper.register_callback(self._get_dump_users, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.GET_DUMP_USERS))
        self.aiogram_wrapper.register_callback(self._send_message_to_user, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.SEND_MESSAGE_TO_USER))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        keyboard_builder = get_keyboard_for_admin_main_menu()
        text_message = ADMIN_MAIN_MENU_MESSAGE
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard_builder.as_markup())

    async def _take_the_survey(self, callback: CallbackQuery, callback_data: AdminMainMenuCallbackFactory, state: FSMContext):
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.TAKE_THE_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        # await self.manager.launch(name="select_take_survey",
        #                           message=callback.message,
        #                           state=state)
        await self.manager.launch(name="take_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=int(TARGETED_SURVEY_ID))
        await callback.answer()

    async def _edit_surveys(self, callback: CallbackQuery, callback_data: AdminMainMenuCallbackFactory, state: FSMContext):
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.EDIT_SURVEYS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_surveys",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    async def _edit_admin_list(self, callback: CallbackQuery, callback_data: AdminMainMenuCallbackFactory, state: FSMContext):
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.EDIT_ADMIN_LIST)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_admin_list",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    async def _get_dump_users(self, callback: CallbackQuery, callback_data: AdminMainMenuCallbackFactory, state: FSMContext):
        users = await self.db.user.get_users()
        users = [list(json.loads(x.model_dump_json()).values()) for x in users]
        headers = ["telegram id", "Полное имя", "Роль"]
        file_path = get_tmp_path(filename="users.xlsx")
        file_path = self.xlsx_handler.create_from_list(data=users,
                                                       headers=headers,
                                                       file_path=file_path)
        await self.aiogram_wrapper.send_file(chat_id=callback.message.chat.id,
                                             file_path=file_path)
        await callback.answer()

    async def _send_message_to_user(self, callback: CallbackQuery, callback_data: AdminMainMenuCallbackFactory, state: FSMContext):
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.SELECT_USER_TO_SEND_MESSAGE)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="select_user_to_send_message",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
