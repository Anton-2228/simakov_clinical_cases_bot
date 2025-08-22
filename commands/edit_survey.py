import json
import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import EditAdminListCallbackFactory, EditSurveyCallbackFactory
from commands import BaseCommand
from db.service.abc_services import ABCServices
from enums import ListEditAdminListActions, USER_TYPE, ListEditSurveyActions, RedisTmpFields
from keyboards_generators import get_keyboard_for_edit_admin_list, get_keyboard_for_edit_survey
from output_generators import create_edit_admin_list_output, create_edit_survey_output
from pagers.aiogram_pager import AiogramPager
from resources.messages import REQUEST_ENTER_NEW_ADMIN_MESSAGE
from states import States

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from commands import Manager

class EditSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._edit_selection, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.EDIT_SELECTION))
        self.aiogram_wrapper.register_callback(self._next_steps, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.NEXT_STEPS))
        self.aiogram_wrapper.register_callback(self._previous_steps, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.PREVIOUS_STEPS))
        self.aiogram_wrapper.register_callback(self._add_step, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.ADD_NEW_STEP))
        self.aiogram_wrapper.register_callback(self._set_steps_order, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.SET_STEPS_ORDER))
        self.aiogram_wrapper.register_callback(self._return, EditSurveyCallbackFactory.filter(F.action == ListEditSurveyActions.RETURN))
        self.steps_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper,
                                        dump_field_name=RedisTmpFields.DUMP_EDIT_SURVEY.value)

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_id: Optional[int] = None,
                      **kwargs):
        survey_steps = await self.db.survey_step.get_all_survey_steps(survey_id=survey_id)
        survey_steps = [json.loads(x.model_dump_json()) for x in survey_steps]
        survey_steps = sorted(survey_steps, key=lambda x: x["position"])
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.EDIT_SURVEY_SURVEY_ID.value,
                                                  value=survey_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.EDIT_SURVEY_LIST_STEPS.value,
                                                  value=survey_steps)
        await self.steps_pager.init(state_context=state, elements=survey_steps, page_count=6)
        page_number, page_status, current_page = await self.steps_pager.get_start_page(state_context=state)
        # current_page = sorted(current_page, key=lambda x: x["id"])
        current_page_idxs = [x["id"] for x in current_page]
        keyboard = get_keyboard_for_edit_survey(steps_idx=current_page_idxs, page_status=page_status)
        text_message = create_edit_survey_output(survey_steps=current_page)
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard.as_markup())

    async def _edit_selection(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_SURVEY_ID.value)

        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEY_STEP)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_survey_step",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id,
                                  step_id=callback_data.step_id)
        await callback.answer()

    async def _next_steps(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        page_number, page_status, current_page = await self.steps_pager.get_next_page(state_context=state)
        # current_page = sorted(current_page, key=lambda x: x["id"])
        current_page_idxs = [x["id"] for x in current_page]
        keyboard = get_keyboard_for_edit_survey(steps_idx=current_page_idxs, page_status=page_status)
        text_message = create_edit_survey_output(survey_steps=current_page)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _previous_steps(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        page_number, page_status, current_page = await self.steps_pager.get_previous_page(state_context=state)
        # current_page = sorted(current_page, key=lambda x: x["id"])
        current_page_idxs = [x["id"] for x in current_page]
        keyboard = get_keyboard_for_edit_survey(steps_idx=current_page_idxs, page_status=page_status)
        text_message = create_edit_survey_output(survey_steps=current_page)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _add_step(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.ADD_STEP)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_SURVEY_ID.value)
        await self.manager.launch(name="add_survey_step",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _set_steps_order(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SET_STEPS_ORDER)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.EDIT_SURVEY_SURVEY_ID.value)
        await self.manager.launch(name="set_steps_order",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _return(self, callback: CallbackQuery, callback_data: EditSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEYS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="edit_surveys",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
