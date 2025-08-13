from functools import wraps
from typing import Any

from aiogram.fsm.context import FSMContext

from aiogram_wrapper import AiogramWrapper
from pagers.pager import Pager


def check_initialized(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.inited:
            state_context = kwargs.get('state_context')
            assert state_context is not None, "Необходимо передавать state_context: FSMContext как аргумент"
            await self.re_init(state_context)
        return await func(self, *args, **kwargs)
    return wrapper

def dump_pager(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        func_result = await func(self, *args, **kwargs)
        state_context = kwargs.get('state_context')
        assert state_context is not None, "Необходимо передавать state_context: FSMContext как аргумент"
        await self.dump(state_context)
        return func_result
    return wrapper


class AiogramPager(Pager):
    def __init__(self, aiogram_wrapper: AiogramWrapper, dump_field_name: str):
        super().__init__()
        self.aiogram_wrapper = aiogram_wrapper
        self.dump_field_name = dump_field_name

    async def re_init(self, state_context: FSMContext):
        dump_object = await self.aiogram_wrapper.get_state_data(state_context=state_context,
                                                                field_name=self.dump_field_name)
        self.elements = dump_object["elements"]
        self.page_count = dump_object["page_count"]
        self.elements_by_page = dump_object["elements_by_page"]
        self.number_of_page = dump_object["number_of_page"]
        self.current_page = dump_object["current_page"]

    async def dump(self, state_context: FSMContext):
        dump_object = {"elements": self.elements,
                       "page_count": self.page_count,
                       "elements_by_page": self.elements_by_page,
                       "number_of_page": self.number_of_page,
                       "current_page": self.current_page}

        await self.aiogram_wrapper.set_state_data(state_context=state_context,
                                                  field_name=self.dump_field_name,
                                                  value=dump_object)

    @dump_pager
    async def init(self, state_context: FSMContext, elements: list[Any], page_count: int):
        return super().init(elements=elements, page_count=page_count)

    @check_initialized
    async def get_page(self, state_context: FSMContext, page_num: int):
        return super().get_page(page_num=page_num)

    @check_initialized
    @dump_pager
    async def get_start_page(self, state_context: FSMContext):
        return super().get_start_page()

    @check_initialized
    @dump_pager
    async def get_next_page(self, state_context: FSMContext):
        return super().get_next_page()

    @check_initialized
    @dump_pager
    async def get_previous_page(self, state_context: FSMContext):
        return super().get_previous_page()
