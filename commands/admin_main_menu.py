import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory, AdminMainMenuCallbackFactory

from db.service.abc_services import ABCServices
from enums import ListUserMainMenuActions, ListAdminMainMenuActions
from keyboards_generators import get_keyboard_for_user_main_menu, get_keyboard_for_admin_main_menu
from resources.messages import USER_MAIN_MENU_MESSAGE, ADMIN_MAIN_MENU_MESSAGE
from states import States
from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class AdminMainMenu(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._add_clinical_case, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.ADD_CLINICAL_CASE))
        self.aiogram_wrapper.register_callback(self._edit_surveys, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.EDIT_SURVEYS))
        self.aiogram_wrapper.register_callback(self._edit_admin_list, AdminMainMenuCallbackFactory.filter(F.action == ListAdminMainMenuActions.EDIT_ADMIN_LIST))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        keyboard_builder = get_keyboard_for_admin_main_menu()
        text_message = ADMIN_MAIN_MENU_MESSAGE
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard_builder.as_markup())

    async def _add_clinical_case(self, callback: CallbackQuery, callback_data: AdminMainMenuCallbackFactory, state: FSMContext):
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ADD_CLINICAL_CASE)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="add_clinical_case",
                                  message=callback.message,
                                  state=state)
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
