from pathlib import Path

from utils import load_txt

HELLO_MESSAGE = load_txt(Path(__file__).parent / "HELLO.txt")
USER_MAIN_MENU_MESSAGE = load_txt(Path(__file__).parent / "USER_MAIN_MENU.txt")
ADMIN_MAIN_MENU_MESSAGE = load_txt(Path(__file__).parent / "ADMIN_MAIN_MENU.txt")
REGISTRATION_MESSAGE = load_txt(Path(__file__).parent / "REGISTRATION.txt")
REGISTRATION_NOT_VALID_FULL_NAME_MESSAGE = load_txt(Path(__file__).parent / "errors/REGISTRATION_NOT_VALID_FULL_NAME.txt")
