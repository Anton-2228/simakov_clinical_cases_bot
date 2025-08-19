import json
import logging
from typing import Optional, TYPE_CHECKING

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import UserMainMenuCallbackFactory, SetStepsOrderCallbackFactory

from db.service.abc_services import ABCServices
from enums import ListUserMainMenuActions, RedisTmpFields, ListSetStepsOrderActions
from keyboards_generators import get_keyboard_for_user_main_menu, get_keyboard_for_set_steps_order
from output_generators import create_set_steps_order_output
from pagers.aiogram_pager import AiogramPager
from resources.messages import USER_MAIN_MENU_MESSAGE, ENTER_NEW_STEPS_ORDER_WRONG_NUMBERS_IDX, \
    ENTER_NEW_STEPS_ORDER_ID_NOT_NUMBER, ENTER_NEW_STEPS_ORDER_ID_NOT_EXIST
from states import States
from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class SetStepsOrder(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._enter_new_steps_order, States.ENTER_NEW_STEPS_ORDER)
        self.aiogram_wrapper.register_callback(self._next_steps, SetStepsOrderCallbackFactory.filter(F.action == ListSetStepsOrderActions.NEXT_STEPS))
        self.aiogram_wrapper.register_callback(self._previous_steps, SetStepsOrderCallbackFactory.filter(F.action == ListSetStepsOrderActions.PREVIOUS_STEPS))
        self.aiogram_wrapper.register_callback(self._keep_current_value, SetStepsOrderCallbackFactory.filter(F.action == ListSetStepsOrderActions.KEEP_CURRENT_VALUE))
        self.steps_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper, dump_field_name=RedisTmpFields.DUMP_SET_STEPS_ORDER.value)

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_id: Optional[int] = None,
                      **kwargs):
        survey_steps = await self.db.survey_step.get_all_survey_steps(survey_id=survey_id)
        survey_steps = [json.loads(x.model_dump_json()) for x in survey_steps]
        survey_steps = sorted(survey_steps, key=lambda x: x["id"])
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SET_STEPS_ORDER_SURVEY_ID.value,
                                                  value=survey_id)
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SET_STEPS_ORDER_LIST_STEPS.value,
                                                  value=survey_steps)
        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.ENTER_NEW_STEPS_ORDER)
        await self.steps_pager.init(state_context=state, elements=survey_steps, page_count=6)
        page_number, page_status, current_page = await self.steps_pager.get_start_page(state_context=state)
        # current_page = sorted(current_page, key=lambda x: x["id"])
        keyboard = get_keyboard_for_set_steps_order(page_status=page_status)
        text_message = create_set_steps_order_output(survey_steps=current_page)
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard.as_markup())

    async def _next_steps(self, callback: CallbackQuery, callback_data: SetStepsOrderCallbackFactory, state: FSMContext):
        page_number, page_status, current_page = await self.steps_pager.get_next_page(state_context=state)
        # current_page = sorted(current_page, key=lambda x: x["id"])
        keyboard = get_keyboard_for_set_steps_order(page_status=page_status)
        text_message = create_set_steps_order_output(survey_steps=current_page)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _previous_steps(self, callback: CallbackQuery, callback_data: SetStepsOrderCallbackFactory, state: FSMContext):
        page_number, page_status, current_page = await self.steps_pager.get_previous_page(state_context=state)
        # current_page = sorted(current_page, key=lambda x: x["id"])
        keyboard = get_keyboard_for_set_steps_order(page_status=page_status)
        text_message = create_set_steps_order_output(survey_steps=current_page)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.aiogram_wrapper.answer_massage(message=callback.message,
                                                                 text=text_message,
                                                                 reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _keep_current_value(self, callback: CallbackQuery, callback_data: SetStepsOrderCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.EDIT_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.SET_STEPS_ORDER_SURVEY_ID.value)

        await self.manager.launch(name="edit_survey",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()

    async def _enter_new_steps_order(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        steps = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                          field_name=RedisTmpFields.SET_STEPS_ORDER_LIST_STEPS.value)

        row_new_steps_order = message.text
        new_steps_order = row_new_steps_order.strip().split()
        if len(new_steps_order) != len(steps):
            await self.aiogram_wrapper.answer_massage(message=message,
                                                      text=ENTER_NEW_STEPS_ORDER_WRONG_NUMBERS_IDX)
            return

        for i in new_steps_order:
            if not i.isdigit():
                await self.aiogram_wrapper.answer_massage(message=message,
                                                          text=ENTER_NEW_STEPS_ORDER_ID_NOT_NUMBER)
                return

        new_steps_order = list(map(int, new_steps_order))

        steps_ids = [int(x["id"]) for x in steps]
        for i in new_steps_order:
            if i not in steps_ids:
                await self.aiogram_wrapper.answer_massage(message=message,
                                                          text=ENTER_NEW_STEPS_ORDER_ID_NOT_EXIST)
                return

        for x, i in enumerate(new_steps_order):
            step = await self.db.survey_step.get_survey_step(id=i)
            step.position = x
            await self.db.survey_step.update_survey_step(survey_step=step)

        await self.aiogram_wrapper.set_state(state_context=state,
                                             state=States.EDIT_SURVEY)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.SET_STEPS_ORDER_SURVEY_ID.value)
        await self.manager.launch(name="edit_survey", message=message, state=state, survey_id=survey_id)
