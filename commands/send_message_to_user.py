import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddSurveyCallbackFactory, SendMessageToAdminCallbackFactory, \
    SendMessageToUserCallbackFactory
from commands import BaseCommand
from db.postgres_models import MessageStatus, MessageType
from db.service.abc_services import ABCServices
from enums import ListAddSurveyListActions, ListSendMessageToAdminActions, ListSendMessageToUserActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_send_message_to_admin, get_keyboard_for_send_message_to_user
from output_generators import create_send_message_to_user_output
from resources.messages import SEND_MESSAGE_TO_ADMIN, SEND_MESSAGE_TO_ADMIN_FINISH, SEND_MESSAGE_TO_USER, \
    SEND_MESSAGE_TO_USER_FINISH
from states import States
from dtos import Message as MessageDTO

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class SendMessageToUser(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_value, States.SEND_MESSAGE_TO_USER)
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, SendMessageToUserCallbackFactory.filter( F.action == ListSendMessageToUserActions.RETURN_TO_MAIN_MENU))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, to_user_id: Optional[int] = None, reply_message_id: Optional[int] = None, **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SEND_MESSAGE_TO_USER_FROM_USER_ID.value,
                                                  value=to_user_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SEND_MESSAGE_TO_USER_REPLY_MESSAGE_ID.value,
                                                  value=reply_message_id)
        user = await self.db.user.get_user(telegram_id=to_user_id)
        text = create_send_message_to_user_output(user=user)
        keyboard = get_keyboard_for_send_message_to_user()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text,
                                                                 reply_markup=keyboard.as_markup())

    async def _enter_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        text = message.text.strip()
        to_user_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                               field_name=RedisTmpFields.SEND_MESSAGE_TO_USER_FROM_USER_ID.value)
        reply_message_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.SEND_MESSAGE_TO_USER_REPLY_MESSAGE_ID.value)
        if reply_message_id:
            reply_message = await self.db.message.get_message(id=reply_message_id)
            reply_message.status = MessageStatus.ANSWERED
            await self.db.message.update_message(message=reply_message)

        message_to_user = MessageDTO(text=text,
                                     from_user_id=message.chat.id,
                                     to_user_id=to_user_id,
                                     status=MessageStatus.NEW,
                                     type=MessageType.TO_USER)
        await self.db.message.save_message(message=message_to_user)
        await self.aiogram_wrapper.answer_massage(message=message,
                                                  text=SEND_MESSAGE_TO_USER_FINISH)
        await self.manager.launch(name="main_menu",
                                  message=message,
                                  state=state)

    async def _return_to_main_menu(self, callback: CallbackQuery, callback_data: SendMessageToAdminCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="main_menu",
                                  message=callback.message,
                                  state=state)
        await callback.answer()


