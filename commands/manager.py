import logging
from typing import Dict, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_wrapper import AiogramWrapper
from commands.base_command import BaseCommand
from db.service.abc_services import ABCServices
from enums import USER_TYPE

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self, db: ABCServices, aiogram_wrapper: AiogramWrapper):
        self.commands_by_role: Dict[USER_TYPE, Dict[str, BaseCommand]] = {}
        for user_type in iter(USER_TYPE):
            self.commands_by_role[user_type] = {}

        self.db = db
        self.aiogram_wrapper = aiogram_wrapper

    def get_commands(self, role: USER_TYPE) -> Dict[str, BaseCommand]:
        return self.commands_by_role[role]

    def add(self, role: USER_TYPE, name: str, command: BaseCommand) -> None:
        self.commands_by_role[role][name] = command

    def update(self, role: USER_TYPE, commands: dict[str, BaseCommand]) -> None:
        for name, command in commands.items():
            self.add(role, name, command)

    async def _launch_command(self, role: USER_TYPE, name: str, message: Message, state: FSMContext, command: Optional[CommandObject] = None):
        assert name in self.commands_by_role[role], (name, self.commands_by_role[role])
        command_ = self.commands_by_role[role][name]
        await command_.execute(message=message, state=state, command=command)

    async def launch(
        self, name: str, message: Message, state: FSMContext, command: Optional[CommandObject] = None
    ) -> None:
        telegram_id = message.chat.id
        user_info = await self.db.user.get_user(telegram_id=telegram_id)
        if not user_info:
            await self._launch_command(role=USER_TYPE.CLIENT, name="registration", message=message,
                                       state=state, command=command)
            return

        await self._launch_command(role=user_info.user_type, name=name, message=message,
                                   state=state, command=command)
