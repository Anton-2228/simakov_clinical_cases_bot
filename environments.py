import os

from dotenv import load_dotenv

load_dotenv()

TEST_MODE=os.getenv("TEST_MODE")
assert TEST_MODE is not None, "TEST_MODE not initialized"

TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
assert TELEGRAM_BOT_TOKEN is not None, "TELEGRAM_BOT_TOKEN not initialized"

REDIS_HOST=os.getenv("REDIS_HOST")
assert REDIS_HOST is not None, "REDIS_HOST not initialized"
REDIS_PORT=os.getenv("REDIS_PORT")
assert REDIS_PORT is not None, "REDIS_PORT not initialized"
REDIS_PASSWORD=os.getenv("REDIS_PASSWORD")
assert REDIS_PASSWORD is not None, "REDIS_PASSWORD not initialized"

POSTGRES_HOST=os.getenv("POSTGRES_HOST")
assert POSTGRES_HOST is not None, "POSTGRES_HOST not initialized"
POSTGRES_PORT=os.getenv("POSTGRES_PORT")
assert POSTGRES_PORT is not None, "POSTGRES_PORT not initialized"
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
assert POSTGRES_PASSWORD is not None, "POSTGRES_PASSWORD not initialized"
POSTGRES_USER=os.getenv("POSTGRES_USER")
assert POSTGRES_USER is not None, "POSTGRES_USER not initialized"
POSTGRES_DB=os.getenv("POSTGRES_DB")
assert POSTGRES_DB is not None, "POSTGRES_DB not initialized"

MINIO_ENDPOINT=os.getenv("MINIO_ENDPOINT")
assert MINIO_ENDPOINT is not None, "MINIO_ENDPOINT not initialized"
MINIO_ROOT_USER=os.getenv("MINIO_ROOT_USER")
assert MINIO_ROOT_USER is not None, "MINIO_ROOT_USER not initialized"
MINIO_ROOT_PASSWORD=os.getenv("MINIO_ROOT_PASSWORD")
assert MINIO_ROOT_PASSWORD is not None, "MINIO_ROOT_PASSWORD not initialized"
MINIO_USER=os.getenv("MINIO_USER")
assert MINIO_USER is not None, "MINIO_USER not initialized"
MINIO_PASSWORD=os.getenv("MINIO_PASSWORD")
assert MINIO_PASSWORD is not None, "MINIO_PASSWORD not initialized"
MINIO_PROD_BUCKET=os.getenv("MINIO_PROD_BUCKET")
assert MINIO_PROD_BUCKET is not None, "MINIO_PROD_BUCKET not initialized"

YANDEX_DISK_TOKEN=os.getenv("YANDEX_DISK_TOKEN")
assert YANDEX_DISK_TOKEN is not None, "YANDEX_DISK_TOKEN not initialized"