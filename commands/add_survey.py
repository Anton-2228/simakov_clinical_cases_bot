import logging
from typing import TYPE_CHECKING, Any, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddSurveyCallbackFactory
from commands import BaseCommand
from db.service.abc_services import ABCServices
from dtos import Survey
from enums import (ListAddSurveyListActions, RedisTmpFields, SURVEY_VARIABLE_FIELDS)
from keyboards_generators import get_keyboard_for_add_survey_field
from output_generators import create_add_survey_output
from resources.messages import (ENTER_NEW_SURVEY_NAME_MAX_SIZE,
                                REQUEST_ENTER_NEW_SURVEY_NAME,
                                REQUEST_ENTER_NEW_SURVEY_START_MESSAGE,
                                REQUEST_ENTER_NEW_SURVEY_FINISH_MESSAGE)
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class AddSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_value, States.ENTER_SURVEY_VALUE)
        self.aiogram_wrapper.register_callback(self._return_to_edit_surveys, AddSurveyCallbackFactory.filter( F.action == ListAddSurveyListActions.RETURN_TO_EDIT_SURVEYS))
        self.field_order = [
            {"field_name": SURVEY_VARIABLE_FIELDS.NAME, "text": REQUEST_ENTER_NEW_SURVEY_NAME},
            {"field_name": SURVEY_VARIABLE_FIELDS.START_MESSAGE, "text": REQUEST_ENTER_NEW_SURVEY_START_MESSAGE},
            {"field_name": SURVEY_VARIABLE_FIELDS.FINISH_MESSAGE, "text": REQUEST_ENTER_NEW_SURVEY_FINISH_MESSAGE}
        ]

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_SURVEY_CURRENT_FIELD_ID.value,
                                                  value=0)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_SURVEY_TEMPLATE_ADDED_SURVEY.value,
                                                  value={})
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ENTER_SURVEY_VALUE)
        text = create_add_survey_output()
        await self.aiogram_wrapper.answer_massage(message=message,
                                                  text=text)
        keyboard = get_keyboard_for_add_survey_field(field=self.field_order[0]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.field_order[0]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state, message=send_message)

    async def _set_template_field(self, state: FSMContext, value: Any):
        template_survey = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                   field_name=RedisTmpFields.ADD_SURVEY_TEMPLATE_ADDED_SURVEY.value)
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_SURVEY_CURRENT_FIELD_ID.value)
        template_survey[self.field_order[current_field_id]["field_name"].value] = value
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_SURVEY_TEMPLATE_ADDED_SURVEY.value,
                                                  value=template_survey)

    async def _get_created_survey(self, state: FSMContext):
        template_survey = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                   field_name=RedisTmpFields.ADD_SURVEY_TEMPLATE_ADDED_SURVEY.value)
        survey = Survey(**template_survey)
        return survey

    async def _save_message_data(self, state: FSMContext, message: Message | SendMessage):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_SURVEY_NAME_REQUEST_MESSAGE_ID.value,
                                                  value=message.message_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_SURVEY_NAME_REQUEST_CHAT_ID.value,
                                                  value=message.chat.id)

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

    async def _set_next_field_id(self, state_context: FSMContext) -> int:
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                     field_name=RedisTmpFields.ADD_SURVEY_CURRENT_FIELD_ID.value)
        current_field_id += 1
        if current_field_id < len(self.field_order):
            await self.aiogram_wrapper.set_state_data(state_context=state_context,
                                                      field_name=RedisTmpFields.ADD_SURVEY_CURRENT_FIELD_ID.value,
                                                      value=current_field_id)
        else:
            current_field_id = -1
        return current_field_id

    async def _send_field_request(self, state_context: FSMContext, message: Message, field_id: int):
        keyboard = get_keyboard_for_add_survey_field(field=self.field_order[field_id]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.field_order[field_id]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state_context, message=send_message)

    async def _end_processing(self, message: Message, state_context: FSMContext):
        survey = await self._get_created_survey(state=state_context)
        await self.db.survey.save_survey(survey=survey)
        await self.aiogram_wrapper.set_state(state_context=state_context,
                                             state=States.EDIT_SURVEYS)
        await self.manager.launch(name="edit_surveys", message=message, state=state_context)

    async def _enter_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_SURVEY_CURRENT_FIELD_ID.value)
        
        if self.field_order[current_field_id]["field_name"] == SURVEY_VARIABLE_FIELDS.NAME:
            survey_name = message.text.strip()
            res_check = await self.aiogram_wrapper._check_validity_of_message(message=message, text=survey_name)
            if res_check:
                return
            if len(survey_name) > 30:
                keyboard = get_keyboard_for_add_survey_field(field=self.field_order[current_field_id]["field_name"])
                send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                         text=ENTER_NEW_SURVEY_NAME_MAX_SIZE,
                                                                         reply_markup=keyboard.as_markup())
                await self._save_message_data(state=state, message=send_message)
                return
            await self._set_template_field(state=state, value=survey_name)
        elif self.field_order[current_field_id]["field_name"] == SURVEY_VARIABLE_FIELDS.START_MESSAGE:
            start_message = message.text.strip()
            res_check = await self.aiogram_wrapper._check_validity_of_message(message=message, text=start_message)
            if res_check:
                return
            await self._set_template_field(state=state, value=start_message)
        elif self.field_order[current_field_id]["field_name"] == SURVEY_VARIABLE_FIELDS.FINISH_MESSAGE:
            finish_message = message.text.strip()
            res_check = await self.aiogram_wrapper._check_validity_of_message(message=message, text=finish_message)
            if res_check:
                return
            await self._set_template_field(state=state, value=finish_message)

        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=message, state_context=state)
            return

        await self._send_field_request(state_context=state, message=message, field_id=current_field_id)

    async def _return_to_edit_surveys(self, callback: CallbackQuery, callback_data: AddSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEYS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_surveys",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
