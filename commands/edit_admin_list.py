import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import EditAdminListCallbackFactory
from commands import BaseCommand
from db.service.services import Services
from enums import ListEditAdminListActions, USER_TYPE
from keyboards_generators import get_keyboard_for_edit_admin_list
from output_generators import create_edit_admin_list_output
from resources.messages import REQUEST_ENTER_NEW_ADMIN_MESSAGE
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class EditAdminList(BaseCommand):
    def __init__(self, manager: "Manager", db: Services, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._add_admin, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.ADD_ADMIN))
        # self.aiogram_wrapper.register_callback(self._remove_admin, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.REMOVE_ADMIN))
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.RETURN_TO_MAIN_MENU))
        # self.aiogram_wrapper.register_callback(self._deletion_selection, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.DELETION_SELECTION))
        # self.aiogram_wrapper.register_callback(self._return_to_edit_admin_list, EditAdminListCallbackFactory.filter(F.action == ListEditAdminListActions.RETURN_TO_EDIT_ADMIN_LIST))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        current_state = await self.aiogram_wrapper.get_state(state_context=state)
        if current_state == States.EDIT_ADMIN_LIST:
            keyboard_builder = get_keyboard_for_edit_admin_list()
            authorized_users = await self.db.user.get_users_by_type(user_type=USER_TYPE.ADMIN)
            output = create_edit_admin_list_output(authorized_users)
            send_message = await self.manager.aiogram_wrapper.answer_massage(message=message,
                                                                             text=output,
                                                                             reply_markup=keyboard_builder.as_markup())

        # elif current_state == States.ENTER_NEW_AUTHORIZED_USERS:
        #     row_users_id = message.text
        #     try:
        #         users_id = list(map(int, row_users_id.split()))
        #     except:
        #         send_message = await self.manager.aiogram_wrapper.answer_massage(message=message,
        #                                                                          text=ERROR_ENTER_NEW_AUTHORIZED_USERS_MESSAGE)
        #         return
        #     adding_users = [Users(telegram_id=user_id,
        #                           authorized_type=AUTHORIZED_TYPE.WHITELIST) for user_id in users_id]
        #     await self.db.users.add_authorized_users(adding_users)
        #     await self.manager.aiogram_wrapper.set_state(state_context=state,
        #                                                  state=States.EDIT_WHITELIST)
        #     await self.manager.launch(name="edit_whitelist",
        #                               message=message,
        #                               state=state)
        #
        # else:
        #     print("Неожиданный state при вызове edit whitelist")

    async def _add_admin(self, callback: CallbackQuery, callback_data: EditAdminListCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.ENTER_NEW_ADMIN)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="add_user_to_admin_list",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    # async def _remove_admin(self, callback: CallbackQuery, callback_data: EditWhitelistCallbackFactory, state: FSMContext):
    #     authorized_users = await self.db.users.get_authorized_users()
    #     keyboard_builder = get_keyboard_for_remove_authorized_users(authorized_users)
    #     send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
    #                                                                      text=REMOVE_AUTHORIZED_USER,
    #                                                                      reply_markup=keyboard_builder.as_markup())
    #     await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
    #                                                       chat_id=callback.from_user.id)
    #     await self.manager.aiogram_wrapper.set_state(state_context=state,
    #                                                  state=States.DELETION_SELECT)
    #
    #     await callback.answer()
    #
    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: EditAdminListCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="main_menu",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
    #
    # async def _deletion_selection(self, callback: CallbackQuery, callback_data: EditWhitelistCallbackFactory, state: FSMContext):
    #     await self.db.users.remove_authorized_user(callback_data.user_id)
    #     await self.manager.aiogram_wrapper.set_state(state_context=state,
    #                                                  state=States.EDIT_WHITELIST)
    #     await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
    #                                                       chat_id=callback.from_user.id)
    #     await self.manager.launch(name="edit_whitelist",
    #                               message=callback.message,
    #                               state=state)
    #     await callback.answer()
    #
    # async def _return_to_edit_admin_list(self, callback: CallbackQuery, callback_data: EditWhitelistCallbackFactory, state: FSMContext):
    #     await self.manager.aiogram_wrapper.set_state(state_context=state,
    #                                                  state=States.EDIT_WHITELIST)
    #     await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
    #                                                       chat_id=callback.from_user.id)
    #     await self.manager.launch(name="edit_whitelist",
    #                               message=callback.message,
    #                               state=state)
    #     await callback.answer()
