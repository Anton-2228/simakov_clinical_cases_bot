import asyncio
import logging
from typing import Optional

from aiogram import Dispatcher
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from init import ROUTER, MANAGER, BOT, COMMANDS, STORAGE
from states import States


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
    dp = Dispatcher(storage=STORAGE)
    dp.include_router(ROUTER)

    await dp.start_polling(BOT)

async def main():
    # await STORAGE.redis.client().flushdb()
    await start_polling()

if __name__ == "__main__":
    asyncio.run(main())
