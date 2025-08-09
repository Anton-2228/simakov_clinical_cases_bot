import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
assert TELEGRAM_BOT_TOKEN is not None, "TELEGRAM_BOT_TOKEN not initialized"

REDIS_HOST=os.getenv("REDIS_HOST")
assert REDIS_HOST is not None, "REDIS_HOST not initialized"
REDIS_PORT=os.getenv("REDIS_PORT")
assert REDIS_PORT is not None, "REDIS_PORT not initialized"
REDIS_PASSWORD=os.getenv("REDIS_PASSWORD")
assert REDIS_PASSWORD is not None, "REDIS_PASSWORD not initialized"
