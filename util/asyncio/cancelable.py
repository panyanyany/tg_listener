import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Cancelable:
    running = False

    def start(self):
        self.running = True

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    async def run(self):
        raise NotImplemented


class CancelableTiktok(Cancelable):
    async def tiktok(self, timeout, tick, timeout_fn):
        """在超时之前，执行 tick，超时后执行 tock"""
        last_time = datetime.now()
        while self.is_running():
            if (datetime.now() - last_time).total_seconds() < timeout:
                await tick()
                await asyncio.sleep(0.1)
            else:
                await timeout_fn()
                last_time = datetime.now()
