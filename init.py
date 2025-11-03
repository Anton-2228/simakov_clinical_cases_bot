from typing import Optional

from aiogram import Bot, Router, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage as TGRedisStorage
from aiogram.types import BotCommand, Message

from aiogram_wrapper import AiogramWrapper
from commands import get_admin_commands, get_user_commands
from commands.manager import Manager
from db.minio.key_builder import SurveyKeyBuilder, KeyBuilderConfig
from db.minio.minio import MinioConfig, AsyncMinioClient
from db.redis import RedisStorage
from db.service.services import Services
from enums import USER_TYPE
from environments import REDIS_HOST, REDIS_PORT, TELEGRAM_BOT_TOKEN, MINIO_ENDPOINT, MINIO_ROOT_PASSWORD, \
    MINIO_PROD_BUCKET, MINIO_ROOT_USER
from states import States

ROUTER = Router()

BOT = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

REDIS = RedisStorage(host=REDIS_HOST, port=REDIS_PORT)
STORAGE = TGRedisStorage(redis=REDIS.redis)
# STORAGE = MemoryStorage()

DISPATCHER = Dispatcher(storage=STORAGE)
DISPATCHER.include_router(ROUTER)

KEY_BUILDER = SurveyKeyBuilder(
    KeyBuilderConfig(
        root=MINIO_PROD_BUCKET,
        date_partition=True,
        hash_sharding=True,
        shard_depth=2,
        shard_size=2,
    )
)
MINIO_CONFIG = MinioConfig(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
    default_bucket=MINIO_PROD_BUCKET,
)
MINIO = AsyncMinioClient(cfg=MINIO_CONFIG, key_builder=KEY_BUILDER)

DB = Services(redis_client=REDIS, minio_client=MINIO)

AIOGRAM_WRAPPER = AiogramWrapper(bot=BOT,
                                 db=DB,
                                 router=ROUTER,
                                 dispatcher=DISPATCHER)

async def command_start(message: Message, state: FSMContext, command: Optional[CommandObject] = None) -> None:
    await MANAGER.launch("start", message, state, command)

async def enter_new_authorized_users(message: Message, state: FSMContext, command: Optional[CommandObject] = None) -> None:
    await MANAGER.aiogram_wrapper.set_state(state, States.MAIN_MENU)
    await MANAGER.launch("main_menu", message, state, command)

AIOGRAM_WRAPPER.register_message_handler(command_start, CommandStart())
AIOGRAM_WRAPPER.register_message_handler(command_start, Command("main_menu"))


MANAGER = Manager(db=DB, aiogram_wrapper=AIOGRAM_WRAPPER)
MANAGER.update(role=USER_TYPE.CLIENT,
               commands=get_user_commands(manager=MANAGER, db=DB, aiogram_wrapper=AIOGRAM_WRAPPER))
MANAGER.update(role=USER_TYPE.ADMIN,
               commands=get_admin_commands(manager=MANAGER, db=DB, aiogram_wrapper=AIOGRAM_WRAPPER))

COMMANDS = [
    BotCommand(command="start", description="Запуск бота"),
    BotCommand(command="main_menu", description="Главное меню")
]
