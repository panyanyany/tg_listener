import asyncio
import logging
from asyncio import Queue, QueueEmpty
from threading import Thread

from hexbytes import HexBytes
from web3 import Web3
from web3.exceptions import BlockNotFound
from web3.middleware import geth_poa_middleware
from web3.types import BlockData

from util.asyncio.cancelable import Cancelable

logger = logging.getLogger(__name__)


class ChainListener(Cancelable):
    def __init__(self, block_number_queue: Queue, w3: Web3 = None, block_queue=None):
        self.w3 = w3
        self.block_number_queue = block_number_queue
        self.block_queue = block_queue or Queue()

    async def loop(self, event_filter, poll_interval):
        while self.is_running():
            try:
                n = self.block_number_queue.get_nowait()
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue
            # 这玩意会卡住
            # for event in event_filter.get_new_entries():
            #     await self.handle_event(event)
            # try:
            #     n = await self.w3.eth.get_block_number()
            # except:
            #     continue
            #
            # if n != latest:
            while self.is_running():
                try:
                    block: BlockData = await self.w3.eth.get_block(n, full_transactions=True)
                    break
                except BlockNotFound:
                    await asyncio.sleep(1)
                    continue
                except BaseException as e:
                    if 'header not found' in str(e):
                        await asyncio.sleep(1)
                        continue
                    logger.error('get block: %s, %s, %s', n, type(e), e)
                    await asyncio.sleep(1)
                    continue
            # logger.info(f'new block: id={n}')
            self.block_queue.put_nowait(block)
            # latest = n
            # await asyncio.sleep(poll_interval)

    async def run(self):
        # block_filter = self.w3.eth.filter('latest')
        await self.loop(None, 0.25)
        logger.info('chain listener stopped')


class BlockNumberListener(Cancelable):
    def __init__(self, w3: Web3 = None):
        self.w3 = w3
        self.queue = Queue()

    async def _run(self):
        latest = 0
        while self.is_running():
            # 这玩意会卡住
            # for event in event_filter.get_new_entries():
            #     await self.handle_event(event)

            if latest == 0:
                try:
                    n = await self.w3.eth.get_block_number()
                    latest = n
                except:
                    continue

            self.queue.put_nowait(latest)
            latest += 1
            await asyncio.sleep(1)
