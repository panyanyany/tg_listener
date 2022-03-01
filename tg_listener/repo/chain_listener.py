import asyncio
import datetime
import queue
from threading import Thread

from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import BlockData


class ChainListener:
    def __init__(self):
        provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
        w3 = Web3(Web3.HTTPProvider(provider))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件
        self.w3 = w3
        self.block_queue = queue.Queue()

    async def handle_event(self, i: HexBytes):
        # block_hash = i.hex()
        while True:
            try:
                block: BlockData = self.w3.eth.get_block(i, full_transactions=True)
                break
            except:
                await asyncio.sleep(0.2)
        self.block_queue.put_nowait(block)
        # dt = datetime.datetime.fromtimestamp(block['timestamp'])
        # print('===== Block hash:  ', i.hex(), block['number'], dt)
        # and whatever

    async def log_loop(self, event_filter, poll_interval):
        while True:
            for event in event_filter.get_new_entries():
                await self.handle_event(event)
            await asyncio.sleep(poll_interval)

    def start(self):
        Thread(target=self.run, daemon=True).start()
        return self.block_queue

    def run(self):
        block_filter = self.w3.eth.filter('latest')
        # tx_filter = w3.eth.filter('pending')
        loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.log_loop(block_filter, 0.25),
            )
        finally:
            loop.close()
