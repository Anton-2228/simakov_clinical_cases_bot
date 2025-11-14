import json
import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import ChangeSurveyCallbackFactory
from db.service.abc_services import ABCServices
from enums import (SURVEY_VARIABLE_FIELDS, ListChangeSurveyActions,
                   RedisTmpFields)
from keyboards_generators import get_keyboard_for_change_survey
from output_generators import create_change_survey_output
from resources.messages import (REQUEST_ENTER_NEW_SURVEY_START_MESSAGE,
                                REQUEST_ENTER_NEW_SURVEY_FINISH_MESSAGE)
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class ChangeSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_new_value, States.ENTER_SURVEY_NEW_VALUE)
        self.aiogram_wrapper.register_callback(self._keep_current_value, ChangeSurveyCallbackFactory.filter(F.action == ListChangeSurveyActions.KEEP_CURRENT_VALUE))
        self.field_order = [{"field_name": SURVEY_VARIABLE_FIELDS.START_MESSAGE, "text": REQUEST_ENTER_NEW_SURVEY_START_MESSAGE},
                            {"field_name": SURVEY_VARIABLE_FIELDS.FINISH_MESSAGE, "text": REQUEST_ENTER_NEW_SURVEY_FINISH_MESSAGE}]

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, survey_id: int = None, **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.CHANGE_SURVEY_SURVEY_ID.value,
                                                  value=survey_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.CHANGE_SURVEY_CURRENT_FIELD_ID.value,
                                                  value=0)
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ENTER_SURVEY_NEW_VALUE)
        survey = await self.db.survey.get_survey(id=survey_id)
        survey = json.loads(survey.model_dump_json())
        text = create_change_survey_output(survey=survey)
        await self.aiogram_wrapper.answer_massage(message=message,
                                                  text=text)
        keyboard = get_keyboard_for_change_survey(field=self.field_order[0]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.field_order[0]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state, message=send_message)

    async def _save_message_data(self, state: FSMContext, message: Message | SendMessage):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_SURVEY_FIELD_VALUE_REQUEST_MESSAGE_ID.value,
                                                  value=message.message_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_SURVEY_FIELD_VALUE_REQUEST_CHAT_ID.value,
                                                  value=message.chat.id)

    async def _get_message_data(self, state: FSMContext) -> tuple[int, int]:
        request_message_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_FIELD_VALUE_REQUEST_MESSAGE_ID.value
        )
        request_chat_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_FIELD_VALUE_REQUEST_CHAT_ID.value
        )
        return request_chat_id, request_message_id

    async def _set_next_field_id(self, state_context: FSMContext) -> int:
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                     field_name=RedisTmpFields.CHANGE_SURVEY_CURRENT_FIELD_ID.value)
        current_field_id += 1
        if current_field_id < len(self.field_order):
            await self.aiogram_wrapper.set_state_data(state_context=state_context,
                                                      field_name=RedisTmpFields.CHANGE_SURVEY_CURRENT_FIELD_ID.value,
                                                      value=current_field_id)
        else:
            current_field_id = -1
        return current_field_id

    async def _send_field_request(self, state_context: FSMContext, message: Message, field_id: int):
        await self._delete_last_message_keyboard(state_context=state_context)
        keyboard = get_keyboard_for_change_survey(field=self.field_order[field_id]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.field_order[field_id]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state_context, message=send_message)

    async def _delete_last_message_keyboard(self, state_context: FSMContext):
        request_chat_id, request_message_id = await self._get_message_data(state=state_context)
        await self.aiogram_wrapper.edit_message_reply_markup(
            chat_id=int(request_chat_id),
            message_id=int(request_message_id),
            reply_markup=None
        )

    async def _end_processing(self, message: Message, state_context: FSMContext):
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                              field_name=RedisTmpFields.CHANGE_SURVEY_SURVEY_ID.value)
        await self._delete_last_message_keyboard(state_context=state_context)
        await self.aiogram_wrapper.set_state(state_context=state_context,
                                             state=States.EDIT_SURVEY)
        await self.manager.launch(name="edit_survey", message=message, state=state_context, survey_id=survey_id)

    async def _keep_current_value(self, callback: CallbackQuery, callback_data: ChangeSurveyCallbackFactory, state: FSMContext):
        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=callback.message, state_context=state)
            return
        await self._send_field_request(state_context=state, message=callback.message, field_id=current_field_id)
        await callback.answer()

    async def _enter_new_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.CHANGE_SURVEY_CURRENT_FIELD_ID.value)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.CHANGE_SURVEY_SURVEY_ID.value)
        
        if self.field_order[current_field_id]["field_name"] == SURVEY_VARIABLE_FIELDS.START_MESSAGE:
            new_start_message = message.text
            res_check = await self.aiogram_wrapper._check_validity_of_message(message=message, text=new_start_message)
            if res_check:
                return
            survey = await self.db.survey.get_survey(id=survey_id)
            survey.start_message = new_start_message
            await self.db.survey.update_survey(survey=survey)
        elif self.field_order[current_field_id]["field_name"] == SURVEY_VARIABLE_FIELDS.FINISH_MESSAGE:
            new_finish_message = message.text
            res_check = await self.aiogram_wrapper._check_validity_of_message(message=message, text=new_finish_message)
            if res_check:
                return
            survey = await self.db.survey.get_survey(id=survey_id)
            survey.finish_message = new_finish_message
            await self.db.survey.update_survey(survey=survey)

        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=message, state_context=state)
            return

        await self._send_field_request(state_context=state, message=message, field_id=current_field_id)
