import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.methods import SendMessage
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import EditAdminListCallbackFactory, EditSurveyCallbackFactory, AddSurveyCallbackFactory
from commands import BaseCommand
from db.service.abc_services import ABCServices
from dtos import Survey
from enums import ListEditAdminListActions, USER_TYPE, ListEditSurveyActions, RedisTmpFields, ListAddSurveyListActions
from keyboards_generators import get_keyboard_for_edit_admin_list, get_keyboard_for_edit_survey, \
    get_keyboard_for_add_survey
from output_generators import create_edit_admin_list_output
from pagers.aiogram_pager import AiogramPager
from resources.messages import REQUEST_ENTER_NEW_ADMIN_MESSAGE, REQUEST_ENTER_NEW_SURVEY_NAME, \
    ENTER_NEW_SURVEY_NAME_MAX_SIZE
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class AddSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_survey_name, States.ADD_SURVEY)
        self.aiogram_wrapper.register_callback(self._return_to_edit_surveys, AddSurveyCallbackFactory.filter( F.action == ListAddSurveyListActions.RETURN_TO_EDIT_SURVEYS))

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.aiogram_wrapper.set_state(state_context=state, state=States.ADD_SURVEY)
        keyboard_builder = get_keyboard_for_add_survey()
        text_message = REQUEST_ENTER_NEW_SURVEY_NAME
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard_builder.as_markup())
        await self._save_message_data(state=state, message=send_message)

    async def _save_message_data(self, state: FSMContext, message: Message | SendMessage):
        await self.aiogram_wrapper.set_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_NAME_REQUEST_MESSAGE_ID.value,
            value=message.message_id
        )
        await self.aiogram_wrapper.set_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_NAME_REQUEST_CHAT_ID.value,
            value=message.chat.id
        )

    async def _get_message_data(self, state: FSMContext) -> tuple[int, int]:
        request_message_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_NAME_REQUEST_MESSAGE_ID.value
        )
        request_chat_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_NAME_REQUEST_CHAT_ID.value
        )
        return request_chat_id, request_message_id

    async def _enter_survey_name(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        request_chat_id, request_message_id = await self._get_message_data(state=state)
        await self.aiogram_wrapper.edit_message_reply_markup(
            chat_id=int(request_chat_id),
            message_id=int(request_message_id),
            reply_markup=None
        )

        survey_name = message.text.strip()
        if len(survey_name) > 30:
            keyboard_builder = get_keyboard_for_add_survey()
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=ENTER_NEW_SURVEY_NAME_MAX_SIZE,
                                                                     reply_markup=keyboard_builder.as_markup())
            await self._save_message_data(state=state, message=send_message)
            return

        survey = Survey(name=survey_name)
        await self.db.survey.save_survey(survey=survey)
        await self.aiogram_wrapper.clear_state(state_context=state)
        await self.manager.launch(name="edit_surveys", message=message, state=state, command=command)

    async def _return_to_edit_surveys(self, callback: CallbackQuery, callback_data: AddSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEYS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_surveys",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
