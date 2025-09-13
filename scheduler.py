import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job
from typing import Callable, Optional
import inspect


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._started = False
        self.tz = ZoneInfo("Europe/Moscow")

    def register_fetcher_cron(self, fetch_job: Callable, second: int | str = None, minute: int | str = None, hour: int | str = None):
        job = self.scheduler.add_job(
            fetch_job,
            trigger=CronTrigger(second=second, minute=minute, hour=hour, timezone=self.tz),
            name=fetch_job.__name__,
            coalesce=True,
            misfire_grace_time=20,
        )

    def register_fetcher_interval(self, fetch_job: Callable, seconds: int | str = 0, minutes: int | str = 0, hours: int | str = 0):
        job = self.scheduler.add_job(
            fetch_job,
            trigger=IntervalTrigger(seconds=seconds, minutes=minutes, hours=hours, timezone=self.tz),
            name=fetch_job.__name__,
            coalesce=True,
            misfire_grace_time=20,
        )

    async def start(self):
        if not self._started:
            self.scheduler.start()
            self._started = True

    async def shutdown(self, wait: bool = True):
        self.scheduler.shutdown(wait=wait)
        self._started = False
