import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory, DeleteUserFromAdminListCallbackFactory

from db.service.abc_services import ABCServices
from enums import ListUserMainMenuActions, USER_TYPE, ListDeleteUserFromAdminListActions
from keyboards_generators import get_keyboard_for_user_main_menu, get_keyboard_for_remove_admins
from resources.messages import USER_MAIN_MENU_MESSAGE, REMOVE_ADMIN_MESSAGE
from states import States
from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class DeleteUserFromAdminLit(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._deletion_selection, DeleteUserFromAdminListCallbackFactory.filter(F.action == ListDeleteUserFromAdminListActions.DELETION_SELECTION))
        self.aiogram_wrapper.register_callback(self._return_to_edit_admin_list, DeleteUserFromAdminListCallbackFactory.filter(F.action == ListDeleteUserFromAdminListActions.RETURN_TO_EDIT_ADMIN_LIST))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.DELETE_USER_FROM_ADMIN_LIST)
        admins = await self.db.user.get_users_by_type(user_type=USER_TYPE.ADMIN)
        me = None
        for admin in admins:
            if admin.telegram_id == message.chat.id:
                me = admin
        admins.remove(me)

        keyboard_builder = get_keyboard_for_remove_admins(admins)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=message,
                                                                         text=REMOVE_ADMIN_MESSAGE,
                                                                         reply_markup=keyboard_builder.as_markup())

    async def _deletion_selection(self, callback: CallbackQuery, callback_data: DeleteUserFromAdminListCallbackFactory, state: FSMContext):
        user = await self.db.user.get_user(telegram_id=callback_data.user_id)
        user.user_type = USER_TYPE.CLIENT
        await self.db.user.update_user(user=user)

        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_ADMIN_LIST)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_admin_list",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    async def _return_to_edit_admin_list(self, callback: CallbackQuery, callback_data: DeleteUserFromAdminListCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_ADMIN_LIST)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_admin_list",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
