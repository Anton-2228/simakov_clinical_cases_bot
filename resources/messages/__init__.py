from pathlib import Path

from utils import load_txt

HELLO_MESSAGE = load_txt(Path(__file__).parent / "HELLO.txt")
