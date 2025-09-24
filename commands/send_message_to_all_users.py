import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import SendMessageToAllUsersCallbackFactory
from commands import BaseCommand
from db.service.abc_services import ABCServices
from enums import ListSendMessageToAllUsersActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_send_message_to_all_users
from output_generators import create_send_message_to_all_users_output
from resources.messages import SEND_MESSAGE_TO_ALL_USERS, SEND_MESSAGE_TO_ALL_USERS_FINISH
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class SendMessageToAllUsers(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_value, States.SEND_MESSAGE_TO_ALL_USERS)
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, SendMessageToAllUsersCallbackFactory.filter(F.action == ListSendMessageToAllUsersActions.RETURN_TO_MAIN_MENU))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        text = create_send_message_to_all_users_output()
        keyboard = get_keyboard_for_send_message_to_all_users()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text,
                                                                 reply_markup=keyboard.as_markup())

    async def _enter_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        users = await self.db.user.get_users()
        
        current_user_id = message.chat.id
        for user in users:
            if user.telegram_id == current_user_id:
                continue
                
            delivered = await self.aiogram_wrapper.send_message_to_user(
                message=message,
                user_telegram_id=user.telegram_id,
                reply_to_message_id=None,
                preserve_forward_header=False,
                attach_markup=True,
            )
        
        await self.aiogram_wrapper.answer_massage(message=message,
                                                  text=SEND_MESSAGE_TO_ALL_USERS_FINISH)
        await self.manager.launch(name="main_menu",
                                  message=message,
                                  state=state)

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: SendMessageToAllUsersCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="main_menu",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
