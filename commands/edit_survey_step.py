import logging
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import EditSurveyStepsCallbackFactory
from commands import BaseCommand
from db.service.abc_services import ABCServices
from enums import (ListEditSurveyStepsActions, RedisTmpFields)
from keyboards_generators import (get_keyboard_for_confirm_delete_step,
                                  get_keyboard_for_edit_survey_step)
from resources.messages import (EDIT_SURVEY_DELETE_STEP,
                                EDIT_SURVEY_STEP)
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class EditSurveyStep(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._change_step, EditSurveyStepsCallbackFactory.filter(F.action == ListEditSurveyStepsActions.CHANGE_STEP))
        self.aiogram_wrapper.register_callback(self._delete_step, EditSurveyStepsCallbackFactory.filter(F.action == ListEditSurveyStepsActions.DELETE_STEP))
        self.aiogram_wrapper.register_callback(self._confirm_delete_step, EditSurveyStepsCallbackFactory.filter(F.action == ListEditSurveyStepsActions.CONFIRM_DELETE_STEP))
        self.aiogram_wrapper.register_callback(self._reject_delete_step, EditSurveyStepsCallbackFactory.filter(F.action == ListEditSurveyStepsActions.REJECT_DELETE_STEP))
        self.aiogram_wrapper.register_callback(self._return_to_edit_survey, EditSurveyStepsCallbackFactory.filter(F.action == ListEditSurveyStepsActions.RETURN_TO_EDIT_SURVEY))

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_id: int = None,
                      step_id: int = None,
                      **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.EDIT_SURVEY_STEPS_SURVEY_ID.value,
                                                  value=survey_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.EDIT_SURVEY_STEPS_STEP_ID.value,
                                                  value=step_id)
        keyboard = get_keyboard_for_edit_survey_step()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=EDIT_SURVEY_STEP,
                                                                 reply_markup=keyboard.as_markup())

    async def _change_step(self, callback: CallbackQuery, callback_data: EditSurveyStepsCallbackFactory, state: FSMContext):
        step_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                            field_name=RedisTmpFields.EDIT_SURVEY_STEPS_STEP_ID.value)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_STEPS_SURVEY_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.CHANGE_SURVEY_STEP)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="change_survey_step",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id,
                                  step_id=step_id)
        await callback.answer()

    async def _delete_step(self, callback: CallbackQuery, callback_data: EditSurveyStepsCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        keyboard = get_keyboard_for_confirm_delete_step()
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=EDIT_SURVEY_DELETE_STEP,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _confirm_delete_step(self, callback: CallbackQuery, callback_data: EditSurveyStepsCallbackFactory, state: FSMContext):
        step_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                            field_name=RedisTmpFields.EDIT_SURVEY_STEPS_STEP_ID.value)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_STEPS_SURVEY_ID.value)
        await self.db.survey_step.delete_step(id=step_id)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _reject_delete_step(self, callback: CallbackQuery, callback_data: EditSurveyStepsCallbackFactory, state: FSMContext):
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_STEPS_SURVEY_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _return_to_edit_survey(self, callback: CallbackQuery, callback_data: EditSurveyStepsCallbackFactory, state: FSMContext):
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_STEPS_SURVEY_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()
