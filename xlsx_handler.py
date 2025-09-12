from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from pathlib import Path
from typing import List, Any, Optional


class XLSXHandler:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_from_list(
        self,
        data: List[List[Any]],
        file_path: str,
        headers: Optional[List[str]] = None
    ) -> Path:
        """
        Создает xlsx-файл из списка списков.
        :param data: [[...], [...], ...]
        :param file_path: путь к создаваемому файлу
        :param headers: список заголовков колонок
        :return: путь к созданному файлу
        """
        wb = Workbook()
        ws = wb.active
        file_path = Path(file_path)

        # Заголовки
        if headers:
            ws.append(headers)
            # Жирный + центрирование по горизонтали и вертикали
            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")
            # Чуть больше высота строки, чтобы центр по вертикали был заметнее
            ws.row_dimensions[1].height = 18

        # Данные
        for row in data:
            ws.append(row)

        # Автоширина колонок
        for col in ws.columns:
            max_len = 0
            first_cell = col[0]
            col_letter = get_column_letter(first_cell.column)
            for cell in col:
                if cell.value is not None:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_len + 2

        wb.save(file_path)
        return file_path