import asyncio
from asyncio import Queue, QueueEmpty
from datetime import datetime

from util.asyncio import cancelable
from util.multicall.async_multicall import AsyncCall, AsyncMulticall
from util.redis import redis_util
from util.web3.util import async_bsc_web3


class ServiceStopped(Exception):
    def __str__(self):
        return f'{self.args[0]} is stopped!'


class BaseService(cancelable.CancelableTiktok):
    def __init__(self):
        self.rdb = redis_util.RedisUtil(prefix=self.__class__.__name__)
        self.queue = Queue()
        self.items = []

    def clear(self):
        self.items.clear()

    def add(self, item):
        if self.rdb.exists(item):
            return True
        self.queue.put_nowait(item)
        return False

    async def load_queue(self):
        while self.queue.qsize():
            self.items.append(self.queue.get_nowait())

    async def get(self, lp_addr, timeout=5):
        """拿信息，没有就等待"""
        if self.rdb.exists(lp_addr):
            return self.rdb.get(lp_addr)

        self.add(lp_addr)

        time_cost = 0
        while self.is_running():
            if time_cost > timeout:
                raise TimeoutError(f"wait for {lp_addr}")
            if self.rdb.exists(lp_addr):
                return self.rdb.get(lp_addr)
            else:
                await asyncio.sleep(0.1)
                time_cost += 0.1
        raise ServiceStopped(self.__class__.__name__)

    async def run(self):
        await self.tiktok(5, self.load_queue, self.batch_process)

    async def batch_process(self):
        raise NotImplemented


class TimedService(cancelable.Cancelable):
    interval = 60

    def __init__(self):
        self.rdb = redis_util.RedisUtil(prefix=self.__class__.__name__)

    async def get(self, lp_addr):
        """拿信息，没有就等待"""
        if self.rdb.exists(lp_addr):
            return self.rdb.get(lp_addr)

        while self.is_running():
            if self.rdb.exists(lp_addr):
                return self.rdb.get(lp_addr)
            else:
                await asyncio.sleep(0.1)
        raise ServiceStopped(self.__class__.__name__)

    async def run(self):
        last_time = None
        while self.is_running():
            if not last_time:
                await self.process()
                last_time = datetime.now()
            elif (datetime.now() - last_time).total_seconds() > self.interval:
                await self.process()
                last_time = datetime.now()
            else:
                await asyncio.sleep(0.1)

    async def process(self):
        raise NotImplemented
