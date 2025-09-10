from __future__ import annotations

import asyncio
import io
import json
import mimetypes
from dataclasses import dataclass
from datetime import timedelta
from typing import AsyncIterator, Iterable, List, Optional

from db.minio.key_builder import SurveyKeyBuilder
from minio import Minio
from minio.error import S3Error, InvalidResponseError


class MinioAsyncError(RuntimeError):
    """Единое исключение обертки. Первопричина в __cause__."""


@dataclass(frozen=True)
class MinioConfig:
    endpoint: str                   # "host:port", напр. "localhost:9000"
    access_key: str
    secret_key: str
    secure: bool = True
    region: Optional[str] = None
    default_bucket: Optional[str] = None
    user_agent: Optional[str] = None


class AsyncMinioClient:
    """
    Асинхронная обертка над MinIO SDK.
    Вызовы MinIO выполняются в thread pool через asyncio.to_thread.
    """

    def __init__(self, cfg: MinioConfig, key_builder: SurveyKeyBuilder) -> None:
        self.key_builder = key_builder
        self._cfg = cfg
        self._client = Minio(
            cfg.endpoint,
            access_key=cfg.access_key,
            secret_key=cfg.secret_key,
            secure=cfg.secure,
            region=cfg.region,
        )
        if cfg.user_agent:
            try:
                self._client._user_agent = f"{self._client._user_agent} {cfg.user_agent}"
            except Exception:
                pass

    # --------- утилиты ---------

    @property
    def default_bucket(self) -> Optional[str]:
        return self._cfg.default_bucket

    def _resolve_bucket(self, bucket: Optional[str]) -> str:
        b = bucket or self._cfg.default_bucket
        if not b:
            raise MinioAsyncError("Не указан bucket и нет default_bucket в конфиге")
        return b

    def _guess_content_type(self, object_name: str, fallback: str = "application/octet-stream") -> str:
        ctype, _ = mimetypes.guess_type(object_name)
        return ctype or fallback

    async def _run(
        self,
        fn,
        *args,
        retries: int = 3,
        backoff_base: float = 0.3,
        **kwargs,
    ):
        attempt = 0
        while True:
            try:
                return await asyncio.to_thread(fn, *args, **kwargs)
            except (S3Error, InvalidResponseError, OSError) as e:
                attempt += 1
                if attempt > retries:
                    raise MinioAsyncError(str(e)) from e
                await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))

    # --------- бакеты ---------

    async def ensure_bucket(self, bucket: Optional[str] = None, make_public: bool = False) -> None:
        b = self._resolve_bucket(bucket)
        exists = await self._run(self._client.bucket_exists, b)
        if not exists:
            await self._run(self._client.make_bucket, b)
        if make_public:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{b}/*"],
                    }
                ],
            }
            await self._run(self._client.set_bucket_policy, b, json.dumps(policy))

    # --------- загрузка ---------

    async def upload_file(
        self,
        object_name: str,
        file_path: str,
        *,
        bucket: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
        retries: int = 3,
    ) -> str:
        b = self._resolve_bucket(bucket)
        ct = content_type or self._guess_content_type(object_name)
        res = await self._run(
            self._client.fput_object,
            b,
            object_name,
            file_path,
            content_type=ct,
            metadata=metadata,
            retries=retries,
        )
        return res.object_name

    async def upload_bytes(
        self,
        object_name: str,
        data: bytes | io.BytesIO,
        *,
        bucket: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
        retries: int = 3,
    ) -> str:
        b = self._resolve_bucket(bucket)
        if isinstance(data, bytes):
            stream = io.BytesIO(data)
            length = len(data)
        else:
            # BytesIO
            pos = data.tell()
            data.seek(0, io.SEEK_END)
            length = data.tell()
            data.seek(pos)
            stream = data

        ct = content_type or self._guess_content_type(object_name)
        res = await self._run(
            self._client.put_object,
            b,
            object_name,
            stream,
            length,
            content_type=ct,
            metadata=metadata,
            retries=retries,
        )
        return res.object_name

    # --------- скачивание ---------

    async def download_file(
        self,
        object_name: str,
        file_path: str,
        *,
        bucket: Optional[str] = None,
        retries: int = 3,
    ) -> None:
        b = self._resolve_bucket(bucket)
        await self._run(self._client.fget_object, b, object_name, file_path, retries=retries)

    async def download_bytes(
        self,
        object_name: str,
        *,
        bucket: Optional[str] = None,
        retries: int = 3,
    ) -> bytes:
        b = self._resolve_bucket(bucket)

        def _get_all() -> bytes:
            resp = self._client.get_object(b, object_name)
            try:
                return resp.read()
            finally:
                resp.close()
                resp.release_conn()

        return await self._run(_get_all, retries=retries)

    # --------- объекты ---------

    async def exists(self, object_name: str, *, bucket: Optional[str] = None) -> bool:
        b = self._resolve_bucket(bucket)
        try:
            await self._run(self._client.stat_object, b, object_name)
            return True
        except MinioAsyncError as e:
            cause = e.__cause__
            if isinstance(cause, S3Error) and cause.code in {"NoSuchKey", "NotFound"}:
                return False
            raise

    async def delete(self, object_name: str, *, bucket: Optional[str] = None) -> None:
        b = self._resolve_bucket(bucket)
        try:
            await self._run(self._client.remove_object, b, object_name)
        except MinioAsyncError as e:
            cause = e.__cause__
            if isinstance(cause, S3Error) and cause.code in {"NoSuchKey", "NotFound"}:
                return
            raise

    async def delete_many(self, object_names: Iterable[str], *, bucket: Optional[str] = None) -> List[str]:
        b = self._resolve_bucket(bucket)

        def _remove_batch(names: Iterable[str]) -> List[str]:
            deleted: List[str] = []
            errors: List[str] = []
            for res in self._client.remove_objects(b, ({"name": n} for n in names)):
                if res.error:
                    errors.append(f"{res.object_name}: {res.error}")
                else:
                    deleted.append(res.object_name)
            if errors:
                raise MinioAsyncError("Часть объектов удалить не удалось:\n" + "\n".join(errors))
            return deleted

        return await self._run(_remove_batch, list(object_names))

    async def list(
        self,
        prefix: Optional[str] = None,
        *,
        bucket: Optional[str] = None,
        recursive: bool = True,
    ) -> AsyncIterator[dict]:
        """
        Async-генератор по объектам.
        Внутри делаем один проход по блокирующему генератору в thread pool.
        Если ожидается очень много объектов — лучше пейджить по префиксам.
        """
        b = self._resolve_bucket(bucket)

        def _collect():
            return list(self._client.list_objects(b, prefix=prefix, recursive=recursive))

        objs = await self._run(_collect)
        for obj in objs:
            yield {
                "name": obj.object_name,
                "size": obj.size,
                "last_modified": getattr(obj, "last_modified", None),
                "etag": getattr(obj, "etag", None),
                "is_dir": getattr(obj, "is_dir", False),
            }

    # --------- ссылки ---------

    async def presign_get(
        self,
        object_name: str,
        *,
        bucket: Optional[str] = None,
        expires: timedelta = timedelta(hours=1),
        req_params: Optional[dict] = None,
    ) -> str:
        b = self._resolve_bucket(bucket)
        # presigned_* не ходят в сеть, но держим единый стиль
        return await self._run(
            self._client.presigned_get_object,
            b,
            object_name,
            expires=expires,
            response_headers=req_params,
        )

    async def presign_put(
        self,
        object_name: str,
        *,
        bucket: Optional[str] = None,
        expires: timedelta = timedelta(minutes=15),
    ) -> str:
        b = self._resolve_bucket(bucket)
        return await self._run(
            self._client.presigned_put_object,
            b,
            object_name,
            expires=expires,
        )

    def object_url(self, object_name: str, *, bucket: Optional[str] = None) -> str:
        """Простая URL. Работает, если бакет публичный."""
        b = self._resolve_bucket(bucket)
        scheme = "https" if self._cfg.secure else "http"
        return f"{scheme}://{self._cfg.endpoint}/{b}/{object_name}"
