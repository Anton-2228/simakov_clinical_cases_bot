import json
import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.methods import SendMessage
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory, EditSurveyStepsCallbackFactory

from db.service.abc_services import ABCServices
from enums import ListUserMainMenuActions, ListEditSurveyStepsActions, SURVEY_STEP_VARIABLE_FILEDS, RedisTmpFields
from keyboards_generators import get_keyboard_for_user_main_menu, get_keyboard_for_edit_survey_steps
from output_generators import create_edit_survey_step_output
from resources.messages import USER_MAIN_MENU_MESSAGE, REQUEST_ENTER_NEW_STEP_NAME, REQUEST_ENTER_NEW_STEP_TEXT, \
    REQUEST_ENTER_NEW_STEP_TYPE
from states import States
from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class EditSurveyStep(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_new_value, States.ENTER_SURVEY_STEP_NEW_VALUE)
        self.aiogram_wrapper.register_callback(self._keep_current_value, EditSurveyStepsCallbackFactory.filter(F.action == ListEditSurveyStepsActions.KEEP_CURRENT_VALUE))
        self.aiogram_wrapper.register_callback(self._set_step_type, EditSurveyStepsCallbackFactory.filter(F.action == ListEditSurveyStepsActions.SELECT_STEP_TYPE))
        self.filed_order = [{"field_name": SURVEY_STEP_VARIABLE_FILEDS.NAME, "text": REQUEST_ENTER_NEW_STEP_NAME},
                            {"field_name": SURVEY_STEP_VARIABLE_FILEDS.TEXT, "text": REQUEST_ENTER_NEW_STEP_TEXT},
                            {"field_name": SURVEY_STEP_VARIABLE_FILEDS.TYPE, "text": REQUEST_ENTER_NEW_STEP_TYPE}]

    async def execute(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None, survey_id: int = None, step_id: int = None, **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.EDIT_SURVEY_STEPS_SURVEY_ID.value,
                                                  value=survey_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.EDIT_SURVEY_STEPS_STEP_ID.value,
                                                  value=step_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.EDIT_SURVEY_STEPS_CURRENT_FIELD_ID.value,
                                                  value=0)
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ENTER_SURVEY_STEP_NEW_VALUE)
        step = await self.db.survey_step.get_survey_step(id=step_id)
        print(survey_id)
        print(step_id)
        print(step)
        step = json.loads(step.model_dump_json())
        text = create_edit_survey_step_output(step=step)
        await self.aiogram_wrapper.answer_massage(message=message,
                                                  text=text)
        keyboard = get_keyboard_for_edit_survey_steps(field=self.filed_order[0]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.filed_order[0]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state, message=send_message)

    async def _save_message_data(self, state: FSMContext, message: Message | SendMessage):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_SURVEY_STEP_FIELD_VALUE_REQUEST_MESSAGE_ID.value,
                                                  value=message.message_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.ENTER_NEW_SURVEY_STEP_FIELD_VALUE_REQUEST_CHAT_ID.value,
                                                  value=message.chat.id)

    async def _get_message_data(self, state: FSMContext) -> tuple[int, int]:
        request_message_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_STEP_FIELD_VALUE_REQUEST_MESSAGE_ID.value
        )
        request_chat_id = await self.aiogram_wrapper.get_state_data(
            state_context=state,
            field_name=RedisTmpFields.ENTER_NEW_SURVEY_STEP_FIELD_VALUE_REQUEST_CHAT_ID.value
        )
        return request_chat_id, request_message_id


    async def _set_next_field_id(self, state_context: FSMContext) -> int:
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                     field_name=RedisTmpFields.EDIT_SURVEY_STEPS_CURRENT_FIELD_ID.value)
        current_field_id += 1
        if current_field_id < len(self.filed_order):
            await self.aiogram_wrapper.set_state_data(state_context=state_context,
                                                      field_name=RedisTmpFields.EDIT_SURVEY_STEPS_CURRENT_FIELD_ID.value,
                                                      value=current_field_id)
        else:
            current_field_id = -1
        return current_field_id

    async def _send_field_request(self, state_context: FSMContext, message: Message, field_id: int):
        await self._delete_last_message_keyboard(state_context=state_context)
        keyboard = get_keyboard_for_edit_survey_steps(field=self.filed_order[field_id]["field_name"])
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=self.filed_order[field_id]["text"],
                                                                 reply_markup=keyboard.as_markup())
        await self._save_message_data(state=state_context, message=send_message)
        # if self.filed_order[field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.NAME:
        #     send_message = await self.aiogram_wrapper.answer_massage(message=message,
        #                                                              text=self.filed_order[field_id]["text"],
        #                                                              reply_markup=keyboard.as_markup())
        #     await self._save_message_data(state=state_context, message=send_message)
        # elif self.filed_order[field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.TEXT:
        #     send_message = await self.aiogram_wrapper.answer_massage(message=message,
        #                                                              text=self.filed_order[field_id]["text"],
        #                                                              reply_markup=keyboard.as_markup())
        #     await self._save_message_data(state=state_context, message=send_message)
        # elif self.filed_order[field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.TYPE:
        #     send_message = await self.aiogram_wrapper.answer_massage(message=message,
        #                                                              text=self.filed_order[field_id]["text"],
        #                                                              reply_markup=keyboard.as_markup())
        #     await self._save_message_data(state=state_context, message=send_message)

    async def _delete_last_message_keyboard(self, state_context: FSMContext):
        request_chat_id, request_message_id = await self._get_message_data(state=state_context)
        await self.aiogram_wrapper.edit_message_reply_markup(
            chat_id=int(request_chat_id),
            message_id=int(request_message_id),
            reply_markup=None
        )

    async def _end_processing(self, message: Message, state_context: FSMContext):
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_STEPS_SURVEY_ID.value)
        await self._delete_last_message_keyboard(state_context=state_context)
        await self.aiogram_wrapper.set_state(state_context=state_context,
                                             state=States.EDIT_SURVEY)
        await self.manager.launch(name="edit_survey", message=message, state=state_context, survey_id=survey_id)

    async def _keep_current_value(self, callback: CallbackQuery, callback_data: EditSurveyStepsCallbackFactory, state: FSMContext):
        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=callback.message, state_context=state)
            return
        await self._send_field_request(state_context=state, message=callback.message, field_id=current_field_id)
        await callback.answer()

    async def _enter_new_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        current_field_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                     field_name=RedisTmpFields.EDIT_SURVEY_STEPS_CURRENT_FIELD_ID.value)
        step_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                            field_name=RedisTmpFields.EDIT_SURVEY_STEPS_STEP_ID.value)
        if self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.NAME:
            new_name = message.text
            step = await self.db.survey_step.get_survey_step(id=step_id)
            step.name = new_name
            await self.db.survey_step.update_survey_step(survey_step=step)
        elif self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.TEXT:
            new_text = message.text
            step = await self.db.survey_step.get_survey_step(id=step_id)
            step.text = new_text
            await self.db.survey_step.update_survey_step(survey_step=step)
        elif self.filed_order[current_field_id]["field_name"] == SURVEY_STEP_VARIABLE_FILEDS.TYPE:
            return

        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=message, state_context=state)
            return

        await self._send_field_request(state_context=state, message=message, field_id=current_field_id)

    async def _set_step_type(self, callback: CallbackQuery, callback_data: EditSurveyStepsCallbackFactory, state: FSMContext):
        new_type = callback_data.step_type
        step_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                            field_name=RedisTmpFields.EDIT_SURVEY_STEPS_STEP_ID.value)
        step = await self.db.survey_step.get_survey_step(id=step_id)
        step.type = new_type
        await self.db.survey_step.update_survey_step(survey_step=step)

        current_field_id = await self._set_next_field_id(state_context=state)
        if current_field_id == -1:
            await self._end_processing(message=callback.message, state_context=state)
            return
        await self._send_field_request(state_context=state, message=callback.message, field_id=current_field_id)
        await callback.answer()
