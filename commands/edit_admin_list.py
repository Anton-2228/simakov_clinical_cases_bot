import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import EditAdminListCallbackFactory
from commands import BaseCommand
from db.service.abc_services import ABCServices
from enums import ListEditAdminListActions, USER_TYPE
from keyboards_generators import get_keyboard_for_edit_admin_list
from output_generators import create_edit_admin_list_output
from resources.messages import REQUEST_ENTER_NEW_ADMIN_MESSAGE
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class EditAdminList(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._add_admin, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.ADD_ADMIN))
        self.aiogram_wrapper.register_callback(self._remove_admin, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.REMOVE_ADMIN))
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.RETURN_TO_MAIN_MENU))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        keyboard_builder = get_keyboard_for_edit_admin_list()
        authorized_users = await self.db.user.get_users_by_type(user_type=USER_TYPE.ADMIN)
        output = create_edit_admin_list_output(authorized_users)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=message,
                                                                         text=output,
                                                                         reply_markup=keyboard_builder.as_markup())

    async def _add_admin(self, callback: CallbackQuery, callback_data: EditAdminListCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.ADD_USER_TO_ADMIN_LIST)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="add_user_to_admin_list",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    async def _remove_admin(self, callback: CallbackQuery, callback_data: EditAdminListCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.DELETE_USER_FROM_ADMIN_LIST)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="delete_user_from_admin_list",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: EditAdminListCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="main_menu",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
