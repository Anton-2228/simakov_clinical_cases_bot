from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class KeyBuilderConfig:
    """
    Настройки структуры ключей.

    root           — корневой префикс для окружения, можно пустую строку.
    users_dir      — сегмент каталога пользователей.
    surveys_dir    — сегмент каталога пройденных опросов.
    files_dir      — сегмент каталога файлов внутри опроса.
    date_partition — добавлять ли YYYY/MM/DD в путь.
    hash_sharding  — добавлять ли шард по хешу (помогает при миллионах файлов в одном префиксе).
    shard_depth    — число уровней шардирования.
    shard_size     — сколько символов хеша на уровень.
    keep_original_filename — оставлять ли оригинальное имя файла в конце ключа.
    """
    root: str = "app"
    users_dir: str = "users"
    surveys_dir: str = "surveys"
    files_dir: str = "files"
    date_partition: bool = False
    hash_sharding: bool = False
    shard_depth: int = 2
    shard_size: int = 2
    keep_original_filename: bool = True


class SurveyKeyBuilder:
    """
    Генерирует стабильные S3-совместимые ключи:
      users/{userId}/surveys/{surveyId}/files/[shards]/[YYYY/MM/DD]/<filename>

    Примеры:
      prefix_user("u1") -> app/users/u1/
      prefix_survey("u1", "s42") -> app/users/u1/surveys/s42/
      prefix_survey_files("u1", "s42") -> app/users/u1/surveys/s42/files/
      key_survey_file("u1", "s42", "результаты.pdf") ->
        app/users/u1/surveys/s42/files/rezultaty.pdf
    """

    def __init__(self, cfg: KeyBuilderConfig | None = None) -> None:
        self.cfg = cfg or KeyBuilderConfig()

    # ---------- публичные методы для префиксов ----------

    def prefix_user(self, user_id: str) -> str:
        """Префикс пользователя для листинга его всего."""
        return self._join(
            self.cfg.root,
            self.cfg.users_dir,
            self._seg(user_id),
            trailing_slash=True,
        )

    def prefix_survey_result(self, user_id: str, survey_id: str) -> str:
        """Префикс конкретного пройденного опроса."""
        return self._join(
            self.cfg.root,
            self.cfg.users_dir,
            self._seg(user_id),
            self.cfg.surveys_dir,
            self._seg(survey_id),
            trailing_slash=True,
        )

    def prefix_survey_result_files(self, user_id: str, survey_id: str) -> str:
        """Префикс каталога файлов внутри опроса. Удобно для list(prefix=...)."""
        return self._join(
            self.prefix_survey_result(user_id, survey_id),
            self.cfg.files_dir,
            trailing_slash=True,
        )

    def prefix_survey_step(self, survey_id: str) -> str:
        return self._join(
            self.cfg.root,
            self.cfg.surveys_dir,
            self._seg(survey_id),
            trailing_slash=True,
        )

    def prefix_survey_step_files(self, survey_id: str) -> str:
        return self._join(
            self.prefix_survey_step(survey_id),
            self.cfg.files_dir,
            trailing_slash=True,
        )

    # ---------- ключи файлов ----------

    def key_survey_file(
        self,
        user_id: str,
        survey_id: str,
        filename: str,
        *,
        category: Optional[str] = None,   # подкаталог типа "attachments", "exports" и т. п.
        ts: Optional[datetime] = None,    # если нужен дата-префикс — можно передать время
        stable_id: Optional[str] = None,  # свой идентификатор файла вместо имени, если нужно
    ) -> str:
        """
        Полный ключ для файла из опроса.
        Пример: app/users/u1/surveys/s42/files/att/20/ab/2025/09/09/report.pdf
        """
        base = [self.prefix_survey_result_files(user_id, survey_id)]
        if category:
            base.append(self._seg(category))

        # шардирование по хешу userId/surveyId/(filename или stable_id)
        if self.cfg.hash_sharding:
            shard_key = f"{user_id}/{survey_id}/{stable_id or filename}"
            base.extend(self._shards(shard_key))

        # дата-партиционирование
        if self.cfg.date_partition:
            dt = ts or datetime.utcnow()
            base.extend([f"{dt:%Y}", f"{dt:%m}", f"{dt:%d}"])

        # финальное имя
        last = self._seg(stable_id) if stable_id else self._file_name(filename)
        return self._join(*base, last)

    def key_survey_step_image(
        self,
        survey_id: str,
        filename: str,
        *,
        category: Optional[str] = None,   # подкаталог типа "attachments", "exports" и т. п.
        ts: Optional[datetime] = None,    # если нужен дата-префикс — можно передать время
        stable_id: Optional[str] = None,  # свой идентификатор файла вместо имени, если нужно
    ) -> str:
        base = [self.prefix_survey_step_files(survey_id)]
        if category:
            base.append(self._seg(category))

        # шардирование по хешу surveyId/(filename или stable_id)
        if self.cfg.hash_sharding:
            shard_key = f"{survey_id}/{stable_id or filename}"
            base.extend(self._shards(shard_key))

        # дата-партиционирование
        if self.cfg.date_partition:
            dt = ts or datetime.utcnow()
            base.extend([f"{dt:%Y}", f"{dt:%m}", f"{dt:%d}"])

        # финальное имя
        last = self._seg(stable_id) if stable_id else self._file_name(filename)
        return self._join(*base, last)

    # ---------- служебные ----------

    _allowed = re.compile(r"[^a-zA-Z0-9._-]+")

    def _seg(self, s: str) -> str:
        # """
        # Делает безопасный сегмент пути:
        #   - нормализует юникод, транслитерирует в ASCII
        #   - режет запрещенные символы, заменяя на '-'
        #   - убирает повторяющиеся дефисы и точки с краев
        # """
        # if not s:
        #     return "_"
        # # нормализация и транслитерация в ASCII
        # norm = unicodedata.normalize("NFKD", s)
        # ascii_bytes = norm.encode("ascii", "ignore")
        # ascii_str = ascii_bytes.decode("ascii") or "_"
        # cleaned = self._allowed.sub("-", ascii_str).strip(" .-/")
        # cleaned = re.sub(r"-{2,}", "-", cleaned)
        # return cleaned or "_"
        return s

    def _file_name(self, name: str) -> str:
        seg = self._seg(name)
        if not self.cfg.keep_original_filename:
            # если не хотим оригинал — можно оставить только безопасную "базу"
            # но чаще полезно сохранить исходное имя
            pass
        return seg or "file"

    def _shards(self, key: str) -> list[str]:
        h = hashlib.sha1(key.encode("utf-8")).hexdigest()
        parts = []
        pos = 0
        for _ in range(self.cfg.shard_depth):
            parts.append(h[pos : pos + self.cfg.shard_size])
            pos += self.cfg.shard_size
        return parts

    def _join(self, *parts: str, trailing_slash: bool = False) -> str:
        """
        Аккуратно склеивает части пути, избегает двойных слешей.
        Поддерживает, что первый аргумент может уже быть полным префиксом.
        """
        # разворачиваем потенциальный первый абсолютный префикс
        flat: list[str] = []
        for p in parts:
            if not p:
                continue
            flat.extend(str(p).split("/"))
        # убираем пустые куски от двойных слешей
        flat = [p for p in flat if p not in ("", None)]
        out = "/".join(flat)
        if trailing_slash and not out.endswith("/"):
            out += "/"
        return out
