import json
import os
import re
import secrets
import tempfile
import uuid
from os import PathLike
from pathlib import Path
from typing import Any, Dict


def load_json(path: PathLike) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def dump_json(data: Any, path: PathLike) -> None:
    with open(path, mode="w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)

def load_txt(path: Path) -> str:
    return path.read_text()

def escape_markdown_v2(text: str) -> str:
    """
    Экранирует все специальные символы MarkdownV2 согласно документации Telegram
    """
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    pattern = re.compile(r'([{}])'.format(re.escape(escape_chars)))
    return pattern.sub(r'\\\1', text)

def get_uuid() -> str:
    return str(uuid.uuid4())

def get_tmp_path() -> str:
    temp_dir = tempfile.mkdtemp()
    random_hex = secrets.token_hex(16)
    temp_file_path = os.path.join(temp_dir, random_hex)
    return temp_file_path