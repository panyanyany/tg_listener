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
            return
        self.queue.put_nowait(item)

    async def get_item(self):
        try:
            self.items += [self.queue.get_nowait()]
            if len(self.items) > 10:
                await self.batch_process()
        except QueueEmpty:
            pass

    async def get(self, lp_addr):
        """拿信息，没有就等待"""
        if self.rdb.exists(lp_addr):
            return self.rdb.get(lp_addr)

        self.add(lp_addr)

        while self.is_running():
            if self.rdb.exists(lp_addr):
                return self.rdb.get(lp_addr)
            else:
                await asyncio.sleep(0.1)
        raise ServiceStopped(self.__class__.__name__)

    async def run(self):
        await self.tiktok(5, self.get_item, self.batch_process)

    async def batch_process(self):
        raise NotImplemented
