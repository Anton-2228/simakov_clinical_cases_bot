import logging

from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage as TGRedisStorage
from aiogram.types import BotCommand

from aiogram_wrapper import AiogramWrapper
from commands import get_user_commands
from commands.manager import Manager
from db.redis import RedisStorage
from db.service.redis_services import RedisServices
from environments import TELEGRAM_BOT_TOKEN

ROUTER = Router()

BOT = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

REDIS = RedisStorage()
STORAGE = TGRedisStorage(redis=REDIS.redis)

DB = RedisServices(redis_client=REDIS)

AIOGRAM_WRAPPER = AiogramWrapper(bot=BOT,
                                 db=DB,
                                 router=ROUTER)

MANAGER = Manager(db=DB, aiogram_wrapper=AIOGRAM_WRAPPER)
MANAGER.update(get_user_commands(manager=MANAGER, db=DB, aiogram_wrapper=AIOGRAM_WRAPPER))

COMMANDS = [
    BotCommand(command="start", description="Запуск бота"),
    BotCommand(command="main_menu", description="Главное меню")
]