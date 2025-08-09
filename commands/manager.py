from typing import Dict, Optional

from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_wrapper import AiogramWrapper
from commands.base_command import BaseCommand
from db.service.services import Services


class Manager:
    def __init__(self, db: Services, aiogram_wrapper: AiogramWrapper):
        self.commands: Dict[str, BaseCommand] = {}
        self.db = db
        self.aiogram_wrapper = aiogram_wrapper

    def get_commands(self) -> Dict[str, BaseCommand]:
        return self.commands

    def add(self, name: str, command: BaseCommand) -> None:
        self.commands[name] = command

    def update(self, commands: dict[str, BaseCommand]) -> None:
        for name, command in commands.items():
            self.add(name, command)

    async def launch(
        self, name: str, message: Message, state: FSMContext, command: Optional[CommandObject] = None
    ) -> None:
        assert name in self.commands, (name, self.commands)
        command_ = self.commands[name]
        await command_.execute(message=message, state=state, command=command)
