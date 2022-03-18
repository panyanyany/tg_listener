import logging
from asyncio import QueueEmpty

from tg_listener.services import base_service
from util.multicall.async_multicall import AsyncCall, AsyncMulticall
from util.web3.util import async_bsc_web3

logger = logging.getLogger(__name__)


class TokenService(base_service.BaseService):
    async def batch_process(self):
        calls = []
        for token in self.items:
            calls += [
                AsyncCall(token, ['decimals()(uint8)', ], [[token, None]]),
            ]
        # logger.info('decimals to cache: %s', len(calls))
        multi = AsyncMulticall(calls, _w3=async_bsc_web3)
        try:
            results = await multi()
        except BaseException as e:
            logger.debug('token service await multi(): %s', e, exc_info=e)
            logger.error('token service await multi(): %s', e)
            return
        for token, decimals in results.items():
            self.rdb.set(token, decimals)

        self.clear()


inst = TokenService()
