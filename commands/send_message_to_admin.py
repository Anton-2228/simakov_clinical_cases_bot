import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddSurveyCallbackFactory, SendMessageToAdminCallbackFactory
from commands import BaseCommand
from db.postgres_models import MessageStatus, MessageType
from db.service.abc_services import ABCServices
from enums import ListAddSurveyListActions, ListSendMessageToAdminActions
from keyboards_generators import get_keyboard_for_send_message_to_admin
from resources.messages import SEND_MESSAGE_TO_ADMIN, SEND_MESSAGE_TO_ADMIN_FINISH
from states import States
from dtos import Message as MessageDTO

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class SendMessageToAdmin(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_value, States.SEND_MESSAGE_TO_ADMIN)
        self.aiogram_wrapper.register_callback(self._return_to_main_menu, SendMessageToAdminCallbackFactory.filter( F.action == ListSendMessageToAdminActions.RETURN_TO_MAIN_MENU))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        keyboard = get_keyboard_for_send_message_to_admin()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=SEND_MESSAGE_TO_ADMIN,
                                                                 reply_markup=keyboard.as_markup())

    async def _enter_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        ask = message.text.strip()
        message_to_admin = MessageDTO(text=ask,
                                      from_user_id=message.chat.id,
                                      status=MessageStatus.NEW,
                                      type=MessageType.TO_ADMINS)
        await self.db.message.save_message(message=message_to_admin)
        await self.aiogram_wrapper.answer_massage(message=message,
                                                  text=SEND_MESSAGE_TO_ADMIN_FINISH)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.MAIN_MENU)
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


