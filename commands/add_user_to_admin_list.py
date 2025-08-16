import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.methods import SendMessage
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory, AddUserToAdminListCallbackFactory

from db.service.abc_services import ABCServices
from enums import ListUserMainMenuActions, USER_TYPE, ListAddUserToAdminListActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_user_main_menu, get_keyboard_for_add_user_to_admin_list
from resources.messages import USER_MAIN_MENU_MESSAGE, REQUEST_ENTER_NEW_ADMIN_MESSAGE, \
    ENTER_NEW_ADMIN_NOT_VALID_TG_ID_MESSAGE, ENTER_NEW_ADMIN_NOT_REGISTERED_USER_MESSAGE
from states import States
from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class AddUserToAdminLit(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_admin_tg_id, States.ENTER_NEW_ADMIN)
        self.aiogram_wrapper.register_callback(self._return_to_edit_admin_list, AddUserToAdminListCallbackFactory.filter(F.action == ListAddUserToAdminListActions.RETURN_TO_EDIT_ADMIN_LIST))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.ENTER_NEW_ADMIN)
        keyboard_builder = get_keyboard_for_add_user_to_admin_list()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=REQUEST_ENTER_NEW_ADMIN_MESSAGE,
                                                                 reply_markup=keyboard_builder.as_markup())
        await self._save_message_data(state=state, message=send_message)

    async def _save_message_data(self, state: FSMContext, message: Message | SendMessage):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_ADMIN_TG_ID_REQUEST_MESSAGE_ID.value,
                                                  value=message.message_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_ADMIN_TG_ID_REQUEST_CHAT_ID.value,
                                                  value=message.chat.id)

    async def _get_message_data(self, state: FSMContext) -> tuple[int, int]:
        request_message_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_ADMIN_TG_ID_REQUEST_MESSAGE_ID.value
        )
        request_chat_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_ADMIN_TG_ID_REQUEST_CHAT_ID.value
        )
        return request_chat_id, request_message_id

    async def _enter_admin_tg_id(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        request_chat_id, request_message_id = await self._get_message_data(state=state)
        await self.aiogram_wrapper.edit_message_reply_markup(
            chat_id=int(request_chat_id),
            message_id=int(request_message_id),
            reply_markup=None
        )
        row_telegram_id = message.text
        if not row_telegram_id.isdigit():
            keyboard_builder = get_keyboard_for_add_user_to_admin_list()
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                      text=ENTER_NEW_ADMIN_NOT_VALID_TG_ID_MESSAGE,
                                                      reply_markup=keyboard_builder.as_markup())
            await self._save_message_data(state=state, message=send_message)
            return
        telegram_id = int(row_telegram_id)
        user = await self.db.user.get_user(telegram_id=telegram_id)
        if not user:
            keyboard_builder = get_keyboard_for_add_user_to_admin_list()
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                      text=ENTER_NEW_ADMIN_NOT_REGISTERED_USER_MESSAGE,
                                                      reply_markup=keyboard_builder.as_markup())
            await self._save_message_data(state=state, message=send_message)
            return

        user.user_type = USER_TYPE.ADMIN
        await self.db.user.update_user(user=user)
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.EDIT_ADMIN_LIST)
        await self.manager.launch(name="edit_admin_list", message=message, state=state, command=command)

    async def _return_to_edit_admin_list(self, callback: CallbackQuery, callback_data: AddUserToAdminListCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_ADMIN_LIST)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_admin_list",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

