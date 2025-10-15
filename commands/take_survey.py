import json
import logging
from typing import TYPE_CHECKING, Callable, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, BufferedInputFile
from aiogram import F
# from magic_filter import F

from aiogram_wrapper import AiogramWrapper
from callbacks_factories import TakeSurveyCallbackFactory
from db.service.abc_services import ABCServices
from db.service.yandex_disk_wrapper import YANDEX_DISK_SESSION
from dtos import SurveyStep, SurveyStepResult, SurveyResult
from enums import (SURVEY_STEP_TYPE, ListTakeSurveyActions,
                   RedisTmpFields, USER_TYPE)
from keyboards_generators import (get_keyboard_for_take_survey,
                                  get_keyboard_for_take_survey_step, get_keyboard_for_send_survey_result_to_admin)
from output_generators import (create_take_survey_file_count_output,
                               create_take_survey_step_output, create_send_info_about_new_survey_result_output)
from pagers.aiogram_pager import AiogramPager
from pagers.pager import PAGING_STATUS
from resources.messages import (TAKE_SURVEY_MAXIMUM_NUMBER_FILES,
                                TAKE_SURVEY_SEND_NOT_FILE,
                                TAKE_SURVEY_START, TAKE_SURVEY_SEND_NOT_TEXT, TAKE_SURVEY_ENTER_FILES_DIRECTION_END,
                                TAKE_SURVEY_WAIT_END, TAKE_SURVEY_SENDED_NOT_ENOUGH_FILES, TAKE_SURVEY_ENTER_FILES_END)
from states import States

from .base_command import BaseCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .manager import Manager

class TakeSurvey(BaseCommand):
    def __init__(self, manager: "Manager", db: ABCServices, aiogram_wrapper: AiogramWrapper) -> None:
        self.max_files_count = 20
        super().__init__(manager, db, aiogram_wrapper)
        self.aiogram_wrapper.register_message_handler(self._finish_send_files, States.PROCESSED_SURVEY,
                                                      F.text.lower() == "✅готово")
        self.aiogram_wrapper.register_message_handler(self._enter_value, States.PROCESSED_SURVEY)
        self.aiogram_wrapper.register_callback(self._return_to_select_take_survey, TakeSurveyCallbackFactory.filter(F.action == ListTakeSurveyActions.RETURN_TO_SELECT_TAKE_SURVEY))
        self.aiogram_wrapper.register_callback(self._start_survey, TakeSurveyCallbackFactory.filter(F.action == ListTakeSurveyActions.START_SURVEY))
        self.steps_pager = AiogramPager(aiogram_wrapper=aiogram_wrapper,
                                        dump_field_name=RedisTmpFields.DUMP_TAKE_SURVEY.value)
        self.processed_answer = {SURVEY_STEP_TYPE.STRING: self._processed_string_answer,
                                 SURVEY_STEP_TYPE.FILES: self._processed_files_answer}

    async def execute(self,
                      message: Message,
                      state: FSMContext,
                      command: Optional[CommandObject] = None,
                      survey_id: Optional[int] = None,
                      **kwargs):
        steps = await self.db.survey_step.get_all_survey_steps(survey_id=survey_id)
        survey = await self.db.survey.get_survey(id=survey_id)
        steps = [{"id": x.id, "position": x.position} for x in steps]
        await self.aiogram_wrapper.set_state_data(state_context=state, field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ANSWER.value,
                                                  value={})
        await self.aiogram_wrapper.set_state_data(state_context=state,
                                                  field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ID.value,
                                                  value=survey_id)
        await self.steps_pager.init(state_context=state, elements=steps, page_count=1)
        keyboard = get_keyboard_for_take_survey()
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=survey.start_message,
                                                                 reply_markup=keyboard.as_markup())
        # send_message = await self.aiogram_wrapper.answer_massage(message=message,
        #                                                          text=TAKE_SURVEY_START,
        #                                                          reply_markup=keyboard.as_markup())

    async def _start_survey(self, callback: CallbackQuery, callback_data: TakeSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.PROCESSED_SURVEY)
        await self.steps_pager.get_start_page(state_context=state)
        await self._send_current_ask(message=callback.message, state_context=state)
        await callback.answer()

    async def _get_current_step(self, state_context: FSMContext) -> SurveyStep:
        page_number, page_status, current_page = await self.steps_pager.get_current_page(state_context=state_context)
        ask = current_page[0]
        current_step = await self.db.survey_step.get_survey_step(id=ask["id"])
        return current_step

    async def _get_next_step(self, state_context: FSMContext) -> SurveyStep:
        page_number, page_status, current_page = await self.steps_pager.get_next_page(state_context=state_context)
        ask = current_page[0]
        current_step = await self.db.survey_step.get_survey_step(id=ask["id"])
        return current_step

    async def _send_current_ask(self, message: Message, state_context: FSMContext):
        step = await self._get_current_step(state_context=state_context)
        text = create_take_survey_step_output(step_type=step.type, step_text=step.text)
        inline_keyboard, reply_keyboard = get_keyboard_for_take_survey_step(step_type=step.type)
        logger.info(step.__dict__)
        if step.image:
            image_bytes = await self.db.files_storage.download_bytes(object_name=step.image)
            image = BufferedInputFile(image_bytes, filename=f"step_{step.id}.png")
            send_message = await self.aiogram_wrapper.answer_photo_massage(message=message,
                                                                           photo=image,
                                                                           caption=text,
                                                                           reply_markup=inline_keyboard.as_markup())
        else:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=text,
                                                                     reply_markup=inline_keyboard.as_markup())
        if step.type == SURVEY_STEP_TYPE.FILES:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_ENTER_FILES_DIRECTION_END,
                                                                     reply_markup=reply_keyboard)

    async def _send_next_ask(self, message: Message, state_context: FSMContext):
        page_number, page_status, current_page = await self.steps_pager.get_current_page(state_context=state_context)
        if page_status in [PAGING_STATUS.LAST_PAGE, PAGING_STATUS.ONLY_PAGE]:
            await self._finish_take_survey(message=message, state_context=state_context)
            return

        step = await self._get_next_step(state_context=state_context)
        text = create_take_survey_step_output(step_type=step.type, step_text=step.text)
        inline_keyboard, reply_keyboard = get_keyboard_for_take_survey_step(step_type=step.type)
        logger.info(step.__dict__)
        if step.image:
            image_bytes = await self.db.files_storage.download_bytes(object_name=step.image)
            image = BufferedInputFile(image_bytes, filename=f"step_{step.id}.png")
            send_message = await self.aiogram_wrapper.answer_photo_massage(message=message,
                                                                           photo=image,
                                                                           caption=text,
                                                                           reply_markup=inline_keyboard.as_markup())
        else:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=text,
                                                                     reply_markup=inline_keyboard.as_markup())
        if step.type == SURVEY_STEP_TYPE.FILES:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_ENTER_FILES_DIRECTION_END,
                                                                     reply_markup=reply_keyboard)

    async def _processed_string_answer(self, message: Message, state_context: FSMContext, step: SurveyStep):
        answer = message.text
        if not answer:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_SEND_NOT_TEXT)
            return

        survey_answer = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                  field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ANSWER.value)
        survey_answer[step.id] = {"answer": answer,
                                  "type": SURVEY_STEP_TYPE.STRING.value}
        await self.aiogram_wrapper.set_state_data(state_context=state_context, field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ANSWER.value,
                                                  value=survey_answer)
        await self._send_next_ask(message=message, state_context=state_context)

    async def _processed_files_answer(self, message: Message, state_context: FSMContext, step: SurveyStep):
        async def _end_processed(survey_answer):
            await self.aiogram_wrapper.set_state_data(state_context=state_context,
                                                      field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ANSWER.value,
                                                      value=survey_answer)
            text = create_take_survey_file_count_output(len(survey_answer[step_id]["answer"]))
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=text)

        doc = message.document
        if not doc:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_SEND_NOT_FILE)
            return

        survey_answer = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                  field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ANSWER.value)
        step_id = str(step.id)
        if step_id not in survey_answer:
            survey_answer[step_id] = {"answer": [],
                                      "type": SURVEY_STEP_TYPE.FILES.value}

        if len(survey_answer[step_id]["answer"]) >= self.max_files_count:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_MAXIMUM_NUMBER_FILES)
            return

        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                              field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ID.value)
        file_s3_path = self.db.files_storage.key_builder.key_survey_file(user_id=str(message.chat.id),
                                                                         survey_id=str(survey_id),
                                                                         filename=doc.file_name)
        tmp_file_path = await self.aiogram_wrapper.download_file(message=message)
        await self.db.files_storage.upload_file(object_name=file_s3_path, file_path=tmp_file_path)
        survey_answer[step_id]["answer"].append(file_s3_path)

        await _end_processed(survey_answer=survey_answer)

    async def _enter_value(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        current_step = await self._get_current_step(state_context=state)
        processed_answer_method: Callable = self.processed_answer[current_step.type]
        assert processed_answer_method is not None, f"Нет обработчика для ответов типа {current_step.type}"
        await processed_answer_method(message=message, state_context=state, step=current_step)

    async def _finish_send_files(self, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        current_step = await self._get_current_step(state_context=state)
        survey_answer = await self.aiogram_wrapper.get_state_data(state_context=state,
                                                                  field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ANSWER.value)
        step_id = str(current_step.id)
        if step_id not in survey_answer:
            send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                     text=TAKE_SURVEY_SENDED_NOT_ENOUGH_FILES)
            return

        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=TAKE_SURVEY_ENTER_FILES_END,
                                                                 reply_markup=ReplyKeyboardRemove())
        await self._send_next_ask(message=message, state_context=state)

    async def _finish_take_survey(self, message: Message, state_context: FSMContext):
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=TAKE_SURVEY_WAIT_END)

        survey_answer = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                  field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ANSWER.value)
        survey_id = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                              field_name=RedisTmpFields.TAKE_SURVEY_SURVEY_ID.value)
        survey_result = SurveyResult(survey_id=int(survey_id),
                                     user_id=message.chat.id)
        survey_result = await self.db.survey_result.save_survey_result(survey_result=survey_result)
        for step_id in survey_answer:
            step_answer = json.dumps(survey_answer[step_id], ensure_ascii=False, indent=2)
            step_result = SurveyStepResult(survey_step_id=int(step_id),
                                           result=step_answer,
                                           survey_result_id=survey_result.id)
            step_result = await self.db.survey_step_result.save_survey_step_result(survey_step_result=step_result)

        survey_result = await self.db.survey_result.get_survey_result(id=survey_result.id)

        async with YANDEX_DISK_SESSION() as yd:
            await yd.add_survey_result(services=self.db, survey_result=survey_result)
            link = await yd.get_folder_link(services=self.db, survey_result=survey_result)
            admins = await self.db.user.get_users_by_type(user_type=USER_TYPE.ADMIN)
            current_user = await self.db.user.get_user(telegram_id=message.chat.id)
            text = create_send_info_about_new_survey_result_output(user=current_user,
                                                                   survey_result=survey_result)
            inline_keyboard = get_keyboard_for_send_survey_result_to_admin(link=link)
            for admin in admins:
                sent_message, new_state = await self.aiogram_wrapper.send_message(
                    text=text,
                    reply_markup=inline_keyboard.as_markup(),
                    chat_id=admin.telegram_id
                )

        survey = await self.db.survey.get_survey(id=survey_id)
        send_message = await self.aiogram_wrapper.answer_massage(message=message,
                                                                 text=survey.finish_message)

        await self.manager.aiogram_wrapper.set_state(state_context=state_context,
                                                     state=States.MAIN_MENU)
        await self.manager.launch(name="main_menu",
                                  message=message,
                                  state=state_context)

    async def _return_to_select_take_survey(self, callback: CallbackQuery, callback_data: TakeSurveyCallbackFactory, state: FSMContext):
        await self.manager.aiogram_wrapper.set_state(state_context=state,
                                                     state=States.SELECT_TAKE_SURVEY)
        await self.manager.aiogram_wrapper.delete_message(message_id=callback.message.message_id,
                                                          chat_id=callback.from_user.id)
        await self.manager.launch(name="select_take_survey",
                                  message=callback.message,
                                  state=state)
        await callback.answer()
