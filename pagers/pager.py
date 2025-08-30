from enum import Enum
from typing import Any


class PAGING_STATUS(Enum):
    FIRST_PAGE = "first_page"
    LAST_PAGE = "last_page"
    INTERMEDIATE_PAGE = "intermediate_page"
    ONLY_PAGE = "only_page"
    NO_PAGE = "no_page"


class Pager:
    def __init__(self):
        self.inited = False

    def init(self, elements: list[Any], page_count: int):
        self.elements = elements
        self.page_count = page_count
        self.elements_by_page = []
        self.number_of_page = 0
        for num in range(0, len(self.elements), self.page_count):
            self.elements_by_page.append(self.elements[num: num + self.page_count])
            self.number_of_page += 1

        self.current_page = None
        self.inited = True

    async def re_init(self, *args, **kwargs):
        """
        Повторная инициализация Pager-а.

        Необходимо задать поля:
            self.elements: list[Any]: список всех элементов
            self.page_count: int: число элементов на странице
            self.elements_by_page: list[tuple[Any] | list[Any]]: разбиение элементов на страницы
            self.number_of_page: int: число страниц
            self.current_page: int: текущая страница

        Args:
            state_context: объект контекста
            dump_field_name: название поля, в котором лежит дамп pager-а
        """

    async def dump(self, *args, **kwargs):
        """
        Метод описывает как pager будет сериализоваться для сохранения в контекст.

        Необходимо сохранить поля:
            self.elements: list[Any]: список всех элементов
            self.page_count: int: число элементов на странице
            self.elements_by_page: list[tuple[Any] | list[Any]]: разбиение элементов на страницы
            self.number_of_page: int: число страниц
            self.current_page: int: текущая страница
        """

    def _get_page(self, page_num: int):
        return self.elements_by_page[page_num]

    def get_page(self, page_num: int):
        return self.elements_by_page[page_num]

    def get_current_page(self):
        if len(self.elements_by_page) == 0:
            return None, PAGING_STATUS.NO_PAGE, []
        if self.number_of_page == 1:
            return self.current_page, PAGING_STATUS.ONLY_PAGE, self._get_page(self.current_page)
        if self.current_page == 0:
            return self.current_page, PAGING_STATUS.FIRST_PAGE, self._get_page(self.current_page)
        if self.current_page + 1 == self.number_of_page:
            return self.current_page, PAGING_STATUS.LAST_PAGE, self._get_page(self.current_page)
        return self.current_page, PAGING_STATUS.INTERMEDIATE_PAGE, self._get_page(self.current_page)

    def get_start_page(self):
        if len(self.elements_by_page) == 0:
            return None, PAGING_STATUS.NO_PAGE, []
        self.current_page = 0
        if self.number_of_page == 1:
            return self.current_page, PAGING_STATUS.ONLY_PAGE, self._get_page(self.current_page)
        return self.current_page, PAGING_STATUS.FIRST_PAGE, self._get_page(self.current_page)

    def get_next_page(self):
        if self.number_of_page == 1:
            return self.current_page, PAGING_STATUS.ONLY_PAGE, self._get_page(self.current_page)
        if self.current_page + 1 == self.number_of_page:
            return self.current_page, PAGING_STATUS.LAST_PAGE, self._get_page(self.current_page)
        self.current_page += 1
        if self.current_page + 1 == self.number_of_page:
            return self.current_page, PAGING_STATUS.LAST_PAGE, self._get_page(self.current_page)
        return self.current_page, PAGING_STATUS.INTERMEDIATE_PAGE, self._get_page(self.current_page)

    def get_previous_page(self):
        if self.number_of_page == 1:
            return self.current_page, PAGING_STATUS.ONLY_PAGE, self._get_page(self.current_page)
        if self.current_page == 0:
            return self.current_page, PAGING_STATUS.FIRST_PAGE, self._get_page(self.current_page)
        self.current_page -= 1
        if self.current_page == 0:
            return self.current_page, PAGING_STATUS.FIRST_PAGE, self._get_page(self.current_page)
        return self.current_page, PAGING_STATUS.INTERMEDIATE_PAGE, self._get_page(self.current_page)
