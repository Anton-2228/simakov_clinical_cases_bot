import logging
from typing import TYPE_CHECKING, Any, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import AddSurveyStepCallbackFactory
from db.service.abc_services import ABCServices
from dtos import SurveyStep
from enums import (SURVEY_STEP_VARIABLE_FILEDS, ListAddSurveyStepActions,
                   RedisTmpFields)
from keyboards_generators import get_keyboard_for_add_survey_steps
from output_generators import create_add_survey_step_output
from resources.messages import (REQUEST_ENTER_STEP_NAME,
                                REQUEST_ENTER_STEP_TEXT,
                                REQUEST_ENTER_STEP_TYPE,
                                REQUEST_ENTER_STEP_IMAGE, ENTER_STEP_IMAGE_NOT_IMAGE)
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class AddSurveyStep(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_value, States.ENTER_SURVEY_STEP_VALUE)
        self.aiogram_wrapper.register_callback(self._set_step_type, AddSurveyStepCallbackFactory.filter(F.action == ListAddSurveyStepActions.SELECT_STEP_TYPE))
        self.aiogram_wrapper.register_callback(self._not_necessary_image, AddSurveyStepCallbackFactory.filter(F.action == ListAddSurveyStepActions.NOT_NECESSARY_IMAGE))
        self.filed_order = [{"field_name": SURVEY_STEP_VARIABLE_FILEDS.NAME, "text": REQUEST_ENTER_STEP_NAME},
                            {"field_name": SURVEY_STEP_VARIABLE_FILEDS.TEXT, "text": REQUEST_ENTER_STEP_TEXT},
                            {"field_name": SURVEY_STEP_VARIABLE_FILEDS.TYPE, "text": REQUEST_ENTER_STEP_TYPE},
                            {"field_name": SURVEY_STEP_VARIABLE_FILEDS.IMAGE, "text": REQUEST_ENTER_STEP_IMAGE}]

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, survey_id: int = None, **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_SURVEY_STEP_SURVEY_ID.value,
                                                  value=survey_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_SURVEY_STEP_CURRENT_FIELD_ID.value,
                                                  value=0)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_SURVEY_STEP_TEMPLATE_ADDED_STEP.value,
                                                  value={})
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ENTER_SURVEY_STEP_VALUE)
        text = create_add_survey_step_output()
        await self.aiogram_wrapper.answer_massage(message=message,
                                                  text=text)
        keyboard = get_keyboard_for_add_survey_steps(field=self.filed_order[0]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.filed_order[0]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state, message=send_message)

    async def _set_template_field(self, state: FSMContext, value: Any):
        template_step = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                  field_name=RedisTmpFields.ADD_SURVEY_STEP_TEMPLATE_ADDED_STEP.value)
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_SURVEY_STEP_CURRENT_FIELD_ID.value)
        if self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.TYPE:
            template_step[self.filed_order[current_field_id]["field_name"].value] = value.value
        else:
            template_step[self.filed_order[current_field_id]["field_name"].value] = value
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ADD_SURVEY_STEP_TEMPLATE_ADDED_STEP.value,
                                                  value=template_step)

    async def _get_created_step(self, state: FSMContext):
        template_step = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                  field_name=RedisTmpFields.ADD_SURVEY_STEP_TEMPLATE_ADDED_STEP.value)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.ADD_SURVEY_STEP_SURVEY_ID.value)
        survey = await self.db.survey.get_survey(id=survey_id)
        all_steps = await self.db.survey_step.get_all_survey_steps(survey_id=survey_id)
        step = SurveyStep(**template_step, position=len(all_steps), survey_id=survey.id)
        return step

    async def _save_message_data(self, state: FSMContext, message: Message | SendMessage):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_SURVEY_STEP_FIELD_VALUE_REQUEST_MESSAGE_ID.value,
                                                  value=message.message_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_SURVEY_STEP_FIELD_VALUE_REQUEST_CHAT_ID.value,
                                                  value=message.chat.id)

    async def _get_message_data(self, state: FSMContext) -> tuple[int, int]:
        request_message_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_SURVEY_STEP_FIELD_VALUE_REQUEST_MESSAGE_ID.value
        )
        request_chat_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_SURVEY_STEP_FIELD_VALUE_REQUEST_CHAT_ID.value
        )
        return request_chat_id, request_message_id


    async def _set_next_field_id(self, state_context: FSMContext) -> int:
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                     field_name=RedisTmpFields.ADD_SURVEY_STEP_CURRENT_FIELD_ID.value)
        current_field_id += 1
        if current_field_id < len(self.filed_order):
            await self.aiogram_wrapper.set_state_data(state_context=state_context,
                                                      field_name=RedisTmpFields.ADD_SURVEY_STEP_CURRENT_FIELD_ID.value,
                                                      value=current_field_id)
        else:
            current_field_id = -1
        return current_field_id

    async def _send_field_request(self, state_context: FSMContext, message: Message, field_id: int):
        keyboard = get_keyboard_for_add_survey_steps(field=self.filed_order[field_id]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.filed_order[field_id]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state_context, message=send_message)

    async def _end_processing(self, message: Message, state_context: FSMContext):
        step = await self._get_created_step(state=state_context)
        await self.db.survey_step.save_survey_step(survey_step=step)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                              field_name=RedisTmpFields.ADD_SURVEY_STEP_SURVEY_ID.value)
        await self.aiogram_wrapper.set_state(state_context=state_context,
                                             state=States.EDIT_SURVEY)
        await self.manager.launch(name="edit_survey", message=message, state=state_context, survey_id=survey_id)

    async def _enter_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.ADD_SURVEY_STEP_CURRENT_FIELD_ID.value)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.ADD_SURVEY_STEP_SURVEY_ID.value)
        if self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.NAME:
            new_name = message.text
            res_check = await self.aiogram_wrapper._check_validity_of_message(message=message, text=new_name)
            if res_check:
                return
            await self._set_template_field(state=state,
                                           value=new_name)
        elif self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.TEXT:
            new_text = message.text
            res_check = await self.aiogram_wrapper._check_validity_of_message(message=message, text=new_text)
            if res_check:
                return
            await self._set_template_field(state=state,
                                           value=new_text)
        elif self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.TYPE:
            return
        elif self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.IMAGE:
            if message.photo:
                file_id = message.photo[-1].file_id
                file_path = await self.aiogram_wrapper.download_file(message=message)
                minio_key = self.db.files_storage.key_builder.key_survey_step_image(survey_id=survey_id,
                                                                                    filename=file_id)
                await self.db.files_storage.upload_file(minio_key, file_path)
                await self._set_template_field(state=state,
                                               value=minio_key)
            else:
                send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                         text=ENTER_STEP_IMAGE_NOT_IMAGE)
                return

        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=message, state_context=state)
            return

        await self._send_field_request(state_context=state, message=message, field_id=current_field_id)

    async def _set_step_type(self, callback: CallbackQuery, callback_data: AddSurveyStepCallbackFactory, state: FSMContext):
        new_type = callback_data.step_type
        await self._set_template_field(state=state,
                                       value=new_type)
        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=callback.message, state_context=state)
            await callback.answer()
            return
        await self._send_field_request(state_context=state, message=callback.message, field_id=current_field_id)
        await callback.answer()

    async def _not_necessary_image(self, callback: CallbackQuery, callback_data: AddSurveyStepCallbackFactory, state: FSMContext):
        await self._set_template_field(state=state,
                                       value=None)
        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=callback.message, state_context=state)
            await callback.answer()
            return
        await self._send_field_request(state_context=state, message=callback.message, field_id=current_field_id)
        await callback.answer()
