import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import SelectSurveyResultCallbackFactory
from db.service.abc_services import ABCServices
from enums import (ListSelectSurveyResultActions, RedisTmpFields)
from keyboards_generators import get_keyboard_for_select_survey_result
from pagers.aiogram_pager import AiogramPager
from resources.messages import SELECT_SURVEY_RESULT
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class SelectSurveyResult(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_callback(self._result_selection, SelectSurveyResultCallbackFactory.filter(F.action == ListSelectSurveyResultActions.RESULT_SELECTION))
        self.aiogram_wrapper.register_callback(self._next_results, SelectSurveyResultCallbackFactory.filter(F.action == ListSelectSurveyResultActions.NEXT_RESULTS))
        self.aiogram_wrapper.register_callback(self._previous_results, SelectSurveyResultCallbackFactory.filter(F.action == ListSelectSurveyResultActions.PREVIOUS_RESULTS))
        self.aiogram_wrapper.register_callback(self._return_to_survey_actions, SelectSurveyResultCallbackFactory.filter(F.action == ListSelectSurveyResultActions.RETURN_TO_SURVEY_ACTIONS))
        self.survey_results_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper,
                                                 dump_field_name=RedisTmpFields.DUMP_SELECT_SURVEY_RESULT.value)

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_id: Optional[int] = None,
                      **kwargs):
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SELECT_SURVEY_RESULT_SURVEY_ID.value,
                                                  value=survey_id)

        # Получаем user_id из сообщения
        user_id = message.chat.id
        
        # Получаем все результаты опросов пользователя для конкретного опроса
        survey_results = await self.db.survey_result.get_survey_results_by_user_and_survey(user_id, survey_id)
        
        # Формируем список текстов для кнопок с датой создания
        survey_results_texts = []
        survey_results_idx_map = {}
        
        for survey_result in survey_results:
            # Форматируем дату для отображения на кнопке
            created_at_str = survey_result.created_at.strftime("%d.%m.%Y %H:%M")
            button_text = f"{survey_result.survey.name} - {created_at_str}"
            
            survey_results_texts.append(button_text)
            survey_results_idx_map[survey_result.id] = button_text
        
        # Сохраняем маппинг в Redis
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.SELECT_SURVEY_RESULT_IDX_MAP.value,
                                                  value=survey_results_idx_map)
        
        # Инициализируем пагинатор
        await self.survey_results_pager.init(state_context=state, elements=survey_results_texts, page_count=5)
        page_number, page_status, current_page = await self.survey_results_pager.get_start_page(state_context=state)
        
        # Создаем клавиатуру
        keyboard = get_keyboard_for_select_survey_result(survey_results=current_page,
                                                         survey_result_idx_map=survey_results_idx_map,
                                                         page_status=page_status)
        
        # Отправляем сообщение
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=SELECT_SURVEY_RESULT,
                                                                 reply_markup=keyboard.as_markup())

    async def _result_selection(self, callback: CallbackQuery, callback_data: SelectSurveyResultCallbackFactory, state: FSMContext):
        survey_result_id = callback_data.survey_result_id
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SURVEY_RESULT_ACTIONS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="survey_result_actions",
                                  message=callback.message,
                                  state=state,
                                  survey_result_id=survey_result_id)
        await callback.answer()

    async def _next_results(self, callback: CallbackQuery, callback_data: SelectSurveyResultCallbackFactory, state: FSMContext):
        survey_results_idx_map = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                           field_name=RedisTmpFields.SELECT_SURVEY_RESULT_IDX_MAP.value)
        page_number, page_status, current_page = await self.survey_results_pager.get_next_page(state_context=state)
        keyboard = get_keyboard_for_select_survey_result(survey_results=current_page,
                                                         survey_result_idx_map=survey_results_idx_map,
                                                         page_status=page_status)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=SELECT_SURVEY_RESULT,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _previous_results(self, callback: CallbackQuery, callback_data: SelectSurveyResultCallbackFactory, state: FSMContext):
        survey_results_idx_map = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                           field_name=RedisTmpFields.SELECT_SURVEY_RESULT_IDX_MAP.value)
        page_number, page_status, current_page = await self.survey_results_pager.get_previous_page(state_context=state)
        keyboard = get_keyboard_for_select_survey_result(survey_results=current_page,
                                                         survey_result_idx_map=survey_results_idx_map,
                                                         page_status=page_status)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        send_message = await self.manager.aiogram_wrapper.answer_massage(message=callback.message,
                                                                         text=SELECT_SURVEY_RESULT,
                                                                         reply_markup=keyboard.as_markup())
        await callback.answer()

    async def _return_to_survey_actions(self, callback: CallbackQuery, callback_data: SelectSurveyResultCallbackFactory, state: FSMContext):
        # Получаем survey_id из состояния, чтобы вернуться к правильному опросу
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                              field_name=RedisTmpFields.SELECT_SURVEY_RESULT_SURVEY_ID.value)
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SURVEY_ACTIONS)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="survey_actions",
                                  message=callback.message,
                                  state=state,
                                  survey_id=survey_id)
        await callback.answer()