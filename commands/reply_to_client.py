import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddSurveyCallbackFactory, SendMessageToAdminCallbackFactory, \
    SendMessageToUserCallbackFactory, ReplyMessageToClientCallbackFactory
from commands import BaseCommand
from db.postgres_models import MessageStatus, MessageType
from db.service.abc_services import ABCServices
from enums import ListAddSurveyListActions, ListSendMessageToAdminActions, ListSendMessageToUserActions, \
    ListReplyMessageToClientActions
from keyboards_generators import get_keyboard_for_send_message_to_admin
from resources.messages import SEND_MESSAGE_TO_ADMIN, SEND_MESSAGE_TO_ADMIN_FINISH
from states import States
from dtos import Message as MessageDTO

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class ReplyMessageToClient(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._reply_to_client, ReplyMessageToClientCallbackFactory.filter( F.action == ListReplyMessageToClientActions.REPLY_TO_CLIENT))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        pass

    async def _reply_to_client(self, callback: CallbackQuery, callback_data: ReplyMessageToClientCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SEND_MESSAGE_TO_USER)
        await self.manager.launch(name="send_message_to_user",
                                  message=callback.message,
                                  state=state,
                                  from_user_id=callback_data.from_user_id)

        await callback.answer()
