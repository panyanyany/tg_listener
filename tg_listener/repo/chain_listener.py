import asyncio
import logging
from asyncio import Queue
from threading import Thread

from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import BlockData

from util.asyncio.cancelable import Cancelable

logger = logging.getLogger(__name__)


class ChainListener(Cancelable):
    def __init__(self, w3: Web3 = None):
        # if not w3:
        #     provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
        #     w3 = Web3(Web3.HTTPProvider(provider))
        #     w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件
        self.w3 = w3
        self.queue = Queue()

    async def handle_event(self, i: HexBytes):
        # block_hash = i.hex()
        while True:
            try:
                block: BlockData = await self.w3.eth.get_block(i, full_transactions=True)
                break
            except:
                await asyncio.sleep(0.2)
        self.queue.put_nowait(block)
        logging.info('got new block')

    async def loop(self, event_filter, poll_interval):
        latest = 0
        while self.is_running():
            # 这玩意会卡住
            # for event in event_filter.get_new_entries():
            #     await self.handle_event(event)
            n = await self.w3.eth.get_block_number()
            if n != latest:
                try:
                    block = await self.w3.eth.get_block(n, full_transactions=True)
                except:
                    continue
                self.queue.put_nowait(block)
                latest = n
            await asyncio.sleep(poll_interval)

    async def run(self):
        # block_filter = self.w3.eth.filter('latest')
        await self.loop(None, 0.25)
        logger.info('chain listener stopped')
