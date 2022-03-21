import logging
from asyncio import QueueEmpty

from tg_listener.services import base_service
from util.bsc.constants import wbnb, cake, multi_call, wbnb_busd_pair, cake_busd_pair
from util.bsc.pancake_swap.multicall import Multicall
from util.multicall.async_multicall import AsyncCall, AsyncMulticall
from util.web3.util import async_bsc_web3, bsc_web3

logger = logging.getLogger(__name__)


class PriceService(base_service.TimedService):
    interval = 5 * 60

    async def get_bnb_price(self):
        return await self.get(wbnb)

    async def get_cake_price(self):
        return await self.get(cake)

    async def process(self):
        try:
            bnb_price = Multicall(web3=bsc_web3).get_bnb_price() / (10 ** 12)
            logger.info('bnb price: %s', bnb_price)
            self.rdb.set(wbnb, bnb_price)

            pair_info = Multicall(web3=bsc_web3).get_pair_info_with_price(cake_busd_pair)
            cake_price = pair_info.token_0.busd_price_human
            logger.info('cake price: %s', cake_price)
            self.rdb.set(cake, cake_price)
        except BaseException as e:
            logger.debug(str(e), exc_info=e)
            logger.warning(str(e))


inst = PriceService()
