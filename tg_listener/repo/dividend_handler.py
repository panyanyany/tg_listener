import asyncio
import logging
from asyncio.queues import Queue, QueueEmpty

from web3 import Web3

from util.asyncio.cancelable import Cancelable
from util.uniswap.trade import Trade

logger = logging.getLogger(__name__)


class DividendHandler(Cancelable):
    """分红币处理"""

    def __init__(self, trade_queue: Queue, w3: Web3):
        self.w3 = w3
        self.trade_queue = trade_queue

    async def run(self):
        token_exists = {}
        while self.is_running():
            try:
                trade: Trade = self.trade_queue.get_nowait()
                # 分红币
                if trade.is_dividend and (trade.price_pair.quote_token not in token_exists):
                    token_exists[trade.price_pair.quote_token] = True
                    logger.info(f'dividend: https://poocoin.app/tokens/{trade.price_pair.quote_token}')
            except QueueEmpty:
                await asyncio.sleep(0.1)
                continue
