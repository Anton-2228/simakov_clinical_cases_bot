import logging

from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage as TGRedisStorage
from aiogram.types import BotCommand

from aiogram_wrapper import AiogramWrapper
from commands import get_user_commands, get_admin_commands
from commands.manager import Manager
from db.redis import RedisStorage
from db.service.services import Services
from enums import USER_TYPE
from environments import TELEGRAM_BOT_TOKEN, REDIS_HOST, REDIS_PORT

ROUTER = Router()

BOT = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

REDIS = RedisStorage(host=REDIS_HOST, port=REDIS_PORT)
STORAGE = TGRedisStorage(redis=REDIS.redis)

DB = Services(redis_client=REDIS)

AIOGRAM_WRAPPER = AiogramWrapper(bot=BOT,
                                 db=DB,
                                 router=ROUTER)

MANAGER = Manager(db=DB, aiogram_wrapper=AIOGRAM_WRAPPER)
MANAGER.update(role=USER_TYPE.CLIENT,
               commands=get_user_commands(manager=MANAGER, db=DB, aiogram_wrapper=AIOGRAM_WRAPPER))
MANAGER.update(role=USER_TYPE.ADMIN,
               commands=get_admin_commands(manager=MANAGER, db=DB, aiogram_wrapper=AIOGRAM_WRAPPER))

COMMANDS = [
    BotCommand(command="start", description="Запуск бота"),
    BotCommand(command="main_menu", description="Главное меню")
]