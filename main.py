import asyncio
import logging
from typing import Optional

from aiogram import Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.postgres import create_tables, drop_tables
from db.service.yandex_disk_wrapper import YANDEX_DISK_SESSION
from dtos import Survey, SurveyStep
from enums import SURVEY_STEP_TYPE, USER_TYPE
from environments import TEST_MODE
from init import BOT, COMMANDS, DB, MANAGER, ROUTER, STORAGE, MINIO, AIOGRAM_WRAPPER, DISPATCHER
from models import User
from regular_tasks import RegularTasks
from scheduler import Scheduler
from states import States
from tests_functions._add_user_to_redis import main as add_user_to_redis

logging.basicConfig(filename="/log/bot.log", filemode="a", level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

@ROUTER.message(CommandStart())
async def command_start(message: Message, state: FSMContext, command: Optional[CommandObject] = None) -> None:
    await MANAGER.launch("start", message, state, command)

@ROUTER.message(Command("main_menu"))
async def enter_new_authorized_users(message: Message, state: FSMContext, command: Optional[CommandObject] = None) -> None:
    await MANAGER.aiogram_wrapper.set_state(state, States.MAIN_MENU)
    await MANAGER.launch("main_menu", message, state, command)

async def start_polling():
    await BOT.set_my_commands(commands=COMMANDS)

    await DISPATCHER.start_polling(BOT)

async def create_test_date():
    await STORAGE.redis.client().flushdb()
    await DB.minio_client.ensure_bucket(bucket=DB.minio_client.default_bucket)
    user = User(telegram_id=173202775,
                full_name="Зинченко Антон Андреевич",
                user_type=USER_TYPE.ADMIN)
    user_id = await DB.user.save_user(user=user)
    async with YANDEX_DISK_SESSION() as yd:
        await yd.mkdir("Зинченко Антон Андреевич")
    # user = User(telegram_id=5613751001,
    #             full_name="Абоба Хуй",
    #             user_type=USER_TYPE.CLIENT)
    # user_id = await DB.user.save_user(user=user)

    await drop_tables()
    await create_tables()

    survey = Survey(name="clinical cases",
                    start_message="Опаааа, стартовое сообщение опроса",
                    finish_message="Оййййй, а это уже финальное сообщение")
    added_survey = await DB.survey.save_survey(survey=survey)

    minio_file_path = MINIO.key_builder.key_survey_file(user_id=user_id, survey_id=str(added_survey.id), filename="aboba")
    await DB.minio_client.upload_file(object_name=minio_file_path,
                                      file_path="./Dockerfile")
    minio_file_path = MINIO.key_builder.key_survey_file(user_id=user_id, survey_id=str(added_survey.id), filename="aboba1")
    await DB.minio_client.upload_file(object_name=minio_file_path,
                                      file_path="./Dockerfile")


    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 0",
                             text="aboba 0 text",
                             position=0,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 1",
                             text="aboba 1 text",
                             position=1,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 2",
                             text="aboba 2 text",
                             position=2,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 3",
                             text="aboba 3 text",
                             position=3,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 4",
                             text="aboba 4 text",
                             position=4,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 5",
                             text="aboba 5 text",
                             position=5,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 6",
                             text="aboba 6 text",
                             position=6,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 7",
                             text="aboba 7 text",
                             position=7,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 8",
                             text="aboba 8 text",
                             position=8,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)






    survey = Survey(name="test survey",
                    start_message="Опаааа, стартовое сообщение опроса",
                    finish_message="Оййййй, а это уже финальное сообщение")
    added_survey = await DB.survey.save_survey(survey=survey)

    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 0",
                             text="aboba 0 text",
                             position=0,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 1",
                             text="aboba 1 text",
                             position=1,
                             type=SURVEY_STEP_TYPE.STRING)
    await DB.survey_step.save_survey_step(survey_step=survey_step)
    survey_step = SurveyStep(survey_id=added_survey.id,
                             name="aboba 2",
                             text="aboba 2 text",
                             position=2,
                             type=SURVEY_STEP_TYPE.FILES)
    await DB.survey_step.save_survey_step(survey_step=survey_step)

async def main():
    if TEST_MODE == "True":
        await create_test_date()
    # scheduler = Scheduler()
    # regular_tasks = RegularTasks(db=DB, aiogram_wrapper=AIOGRAM_WRAPPER, manager=MANAGER)
    # scheduler.register_fetcher_interval(fetch_job=regular_tasks.send_messages_to_admins, seconds=5)
    # scheduler.register_fetcher_interval(fetch_job=regular_tasks.send_messages_to_users, seconds=5)
    # await scheduler.start()


    await start_polling()

if __name__ == "__main__":
    asyncio.run(main())
