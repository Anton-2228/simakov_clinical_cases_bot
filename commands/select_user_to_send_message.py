import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import SelectUserToSendMessageCallbackFactory
from db.service.abc_services import ABCServices
from enums import (ListSelectUserToSendMessageActions, RedisTmpFields)
from keyboards_generators import get_keyboard_for_select_user_to_send_message
from pagers.aiogram_pager import AiogramPager
from resources.messages import SELECT_USER_TO_SEND_MESSAGE
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class SelectUserToSendMessage(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._user_selection, SelectUserToSendMessageCallbackFactory.filter(F.action == ListSelectUserToSendMessageActions.USER_SELECTION))
        self.aiogram_wrapper.register_callback(self._next_users, SelectUserToSendMessageCallbackFactory.filter(F.action == ListSelectUserToSendMessageActions.NEXT_USERS))
        self.aiogram_wrapper.register_callback(self._previous_users, SelectUserToSendMessageCallbackFactory.filter(F.action == ListSelectUserToSendMessageActions.PREVIOUS_USERS))
        self.aiogram_wrapper.register_callback(self._send_to_all_users, SelectUserToSendMessageCallbackFactory.filter(F.action == ListSelectUserToSendMessageActions.SEND_TO_ALL_USERS))
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, SelectUserToSendMessageCallbackFactory.filter(F.action == ListSelectUserToSendMessageActions.RETURN_TO_MAIN_MENU))
        self.users_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper,
                                       dump_field_name=RedisTmpFields.DUMP_SELECT_USER_TO_SEND_MESSAGE.value)

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        users = await self.db.user.get_users()
        me = None
        for user in users:
            if user.telegram_id == message.chat.id:
                me = user
        users.remove(me)

        users_names = []
        users_idx_map = {}
        for user in users:
            user_display_name = f"{user.full_name} (ID: {user.telegram_id})"
            users_names.append(user_display_name)
            users_idx_map[user.telegram_id] = user_display_name
        await self.aiogram_wrapper.set_state_data(state_context=state, field_name=RedisTmpFields.SELECT_USER_TO_SEND_MESSAGE_IDX_MAP.value,
                                                  value=users_idx_map)
        await self.users_pager.init(state_context=state, elements=users_names, page_count=5)
        page_number, page_status, current_page = await self.users_pager.get_start_page(state_context=state)
        keyboard = get_keyboard_for_select_user_to_send_message(users=current_page, user_idx_map=users_idx_map, page_status=page_status)
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                text=SELECT_USER_TO_SEND_MESSAGE,
                                                                reply_markup=keyboard.as_markup())

    async def _user_selection(self, callback: CallbackQuery, callback_data: SelectUserToSendMessageCallbackFactory, state: FSMContext):
        user_id = callback_data.user_id
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SEND_MESSAGE_TO_USER)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="send_message_to_user",
                                  message=callback.message,
                                  state=state,
                                  to_user_id=user_id)
        await callback.answer()

    async def _next_users(self, callback: CallbackQuery, callback_data: SelectUserToSendMessageCallbackFactory, state: FSMContext):
        users_idx_map = await self.aiogram_wrapper.get_state_data(state_context=state, field_name=RedisTmpFields.SELECT_USER_TO_SEND_MESSAGE_IDX_MAP.value)
        page_number, page_status, current_page = await self.users_pager.get_next_page(state_context=state)
        keyboard = get_keyboard_for_select_user_to_send_message(users=current_page, user_idx_map=users_idx_map, page_status=page_status)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=SELECT_USER_TO_SEND_MESSAGE,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _previous_users(self, callback: CallbackQuery, callback_data: SelectUserToSendMessageCallbackFactory, state: FSMContext):
        users_idx_map = await self.aiogram_wrapper.get_state_data(state_context=state, field_name=RedisTmpFields.SELECT_USER_TO_SEND_MESSAGE_IDX_MAP.value)
        page_number, page_status, current_page = await self.users_pager.get_previous_page(state_context=state)
        keyboard = get_keyboard_for_select_user_to_send_message(users=current_page, user_idx_map=users_idx_map, page_status=page_status)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=SELECT_USER_TO_SEND_MESSAGE,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _send_to_all_users(self, callback: CallbackQuery, callback_data: SelectUserToSendMessageCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SEND_MESSAGE_TO_ALL_USERS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="send_message_to_all_users",
                                  message=callback.message,
                                  state=state)
        await callback.answer()

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: SelectUserToSendMessageCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="main_menu",
                                  message=callback.message,
                                  state=state)
        await callback.answer()