import json
import logging
import os
import secrets
import tempfile
import traceback
from pathlib import Path
from typing import Dict
from urllib.parse import quote

import httpx
from yadisk import AsyncClient
from yadisk.sessions.async_httpx_session import AsyncHTTPXSession
from yadisk.types import AsyncFileOrPath
from yadisk.objects import AsyncResourceLinkObject

from db.minio.minio import AsyncMinioClient
from db.service.abc_services import ABCServices
from dtos import SurveyResult, SurveyResultComments
from enums import SURVEY_STEP_TYPE, SURVEY_RESULT_COMMENT_TYPE
from environments import YANDEX_DISK_TOKEN
from resources.result_survey import TXT_STEP_RESULTS_SURVEY, TXT_RESULTS_SURVEY
from utils import get_tmp_path


logger = logging.getLogger(__name__)



class YandexDiskWrapper(AsyncClient):
    def __init__(self, token: str, root_dir: str, *args, **kwargs):
        session = AsyncHTTPXSession(
            timeout=httpx.Timeout(
                connect=20.0,
                read=120.0,
                write=120.0,
                pool=60.0,
            ),
            limits=httpx.Limits(
                max_connections=10,
                max_keepalive_connections=5,
                keepalive_expiry=30.0,
            ),
            http2=False,
            trust_env=True,
            # transport=httpx.AsyncHTTPTransport(retries=0),  # по желанию
        )
        super().__init__(token=token, *args, session=session, **kwargs)
        self.root_dir = root_dir

    async def __aenter__(self):
        await super().__aenter__()
        await self.mkdir(self.root_dir)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def mkdir(
        self,
        path,
        *args,
        **kwargs
    ):
        try:
            path = Path(self.root_dir) / path
            await super().mkdir(str(path), *args, **kwargs)
        except:
            pass

    async def exists(
        self,
        path,
        *args,
        **kwargs
    ) -> bool:
        path = Path(self.root_dir) / path
        return await super().exists(str(path), *args, **kwargs)

    async def upload(
            self,
            path_or_file: AsyncFileOrPath,
            dst_path: str,
            *args,
            **kwargs
    ) -> AsyncResourceLinkObject:
        # убеждаемся, что все поддиректории существуют
        dst_path_obj = Path(dst_path)
        dir_path = dst_path_obj.parent
        if str(dir_path) not in ("", "."):
            current = Path()
            for part in dir_path.parts:
                current /= part
                await self.mkdir(str(current))

        full_dst_path = Path(self.root_dir) / dst_path_obj
        return await super().upload(path_or_file, str(full_dst_path), *args, **kwargs)

    async def create_user_dir(self, full_name):
        await self.mkdir(full_name)

    def _create_string_answers(self, survey_result: SurveyResult):
        def _get_survey_step(step_id: int):
            for step in survey.survey_steps:
                if int(step.id) == int(step_id):
                    return step

        survey = survey_result.survey
        text_answers = ""
        for survey_step_result in survey_result.survey_step_results:
            survey_step = _get_survey_step(step_id=survey_step_result.survey_step_id)
            result = json.loads(survey_step_result.result)
            if result["type"] == SURVEY_STEP_TYPE.FILES.value:
                continue
            ask = survey_step.text
            answer = result["answer"]
            text_answers += f"{TXT_STEP_RESULTS_SURVEY.format(answer=answer)}\n"

        return TXT_RESULTS_SURVEY.format(answers=text_answers)

    async def add_survey_result(self, services: ABCServices, survey_result: SurveyResult):
        async def _check_exists(dst_dir: str, filename: str):
            while True:
                try:
                    file_exists = await self.exists(f"{dst_dir}/{filename}")
                except Exception as e:
                    logger.info(traceback.format_exc())
                    file_exists = False
                if not file_exists:
                    break
                name, ext = os.path.splitext(filename)
                filename = f"{name}_new{ext}"
            return filename

        async def _add_string_result(dst_dir: str):
            string_answers = self._create_string_answers(survey_result)
            temp_file_path = get_tmp_path()
            with open(temp_file_path, 'w') as f:
                f.write(string_answers)
            dst_path = f"{dst_dir}/Ответы.txt"
            await self.upload(temp_file_path, dst_path)

        async def _add_files_result(dst_dir):
            for survey_step_result in survey_result.survey_step_results:
                result = json.loads(survey_step_result.result)
                if result["type"] != SURVEY_STEP_TYPE.FILES.value:
                    continue
                for minio_path in result["answer"]:
                    temp_file_path = get_tmp_path()
                    await services.files_storage.download_file(object_name=minio_path, file_path=temp_file_path)
                    filename = minio_path.split("/")[-1]
                    filename = await _check_exists(dst_dir=dst_dir, filename=filename)
                    dst_path = f"{dst_dir}/{filename}"

                    await self.upload(temp_file_path, dst_path)

        user = await services.user.get_user(telegram_id=survey_result.user_id)
        survey_dir = f"{user.full_name}/{survey_result.survey.name}"
        await self.mkdir(path=survey_dir)
        dst_dir = f"{survey_dir}/{survey_result.created_at}"
        await self.mkdir(path=dst_dir)

        await _add_string_result(dst_dir)
        await _add_files_result(dst_dir)

    async def add_files_to_survey_result(self, services: ABCServices, survey_result: SurveyResult, comment: SurveyResultComments):
        result = json.loads(comment.result)
        if result["type"] == SURVEY_RESULT_COMMENT_TYPE.STRING.value:
            return

        user = await services.user.get_user(telegram_id=survey_result.user_id)
        survey_dir = f"{user.full_name}/{survey_result.survey.name}"
        await self.mkdir(path=survey_dir)
        dst_dir = f"{survey_dir}/{survey_result.created_at}"
        await self.mkdir(path=dst_dir)

        for minio_path in result["answer"]:
            temp_file_path = get_tmp_path()
            await services.files_storage.download_file(object_name=minio_path, file_path=temp_file_path)
            dst_path = f"{dst_dir}/{minio_path.split('/')[-1]}"
            await self.upload(temp_file_path, dst_path)

    async def add_comment_to_survey_result(self, services: ABCServices, survey_result: SurveyResult, comment: SurveyResultComments):
        result = json.loads(comment.result)
        if result["type"] == SURVEY_RESULT_COMMENT_TYPE.FILES.value:
            return

        user = await services.user.get_user(telegram_id=survey_result.user_id)
        survey_dir = f"{user.full_name}/{survey_result.survey.name}"
        await self.mkdir(path=survey_dir)
        dst_dir = f"{survey_dir}/{survey_result.created_at}"
        await self.mkdir(path=dst_dir)

        comment_name = f"Комментарий от {comment.created_at}.txt"

        temp_file_path = get_tmp_path()
        with open(temp_file_path, 'w') as f:
            f.write(result["answer"])
        dst_path = f"{dst_dir}/{comment_name}"
        await self.upload(temp_file_path, dst_path)

    async def delete_survey_result(
            self,
            services: ABCServices,
            survey_result: SurveyResult,
            permanently: bool = True,
    ) -> None:
        user = await services.user.get_user(telegram_id=survey_result.user_id)
        survey_dir = f"{user.full_name}/{survey_result.survey.name}"
        dst_dir = f"{survey_dir}/{survey_result.created_at}"

        full_path = str(Path(self.root_dir) / dst_dir)
        try:
            await super().get_meta(full_path)
        except Exception:
            return

        try:
            await super().remove(full_path, permanently=permanently)
        except Exception:
            pass

    async def get_folder_link(self, services: ABCServices, survey_result: SurveyResult) -> str:
        """
        Вернуть ссылку на папку в веб-интерфейсе Яндекс.Диска.
        Работает только для владельца аккаунта (нужна авторизация).
        """
        user = await services.user.get_user(telegram_id=survey_result.user_id)
        survey_dir = f"{user.full_name}/{survey_result.survey.name}"
        await self.mkdir(path=survey_dir)
        dst_dir = f"{self.root_dir}/{survey_dir}/{survey_result.created_at}"
        # В интерфейсе "disk" всегда начинается с /disk/
        # убираем возможные // и нормализуем
        ydisk_path = str(dst_dir).lstrip("/")
        # encoded_path = "/".join(quote(p) for p in ydisk_path.split("/"))
        encoded_path = quote(ydisk_path, safe="/")
        return f"https://disk.yandex.ru/client/disk/{encoded_path}"

def YANDEX_DISK_SESSION():
    return YandexDiskWrapper(token=YANDEX_DISK_TOKEN, root_dir="/surveys results")
