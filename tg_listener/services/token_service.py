import logging
from asyncio import QueueEmpty

from tg_listener.services import base_service
from util.multicall.async_multicall import AsyncCall, AsyncMulticall
from util.web3.util import async_bsc_web3

logger = logging.getLogger(__name__)


class TokenService(base_service.BaseService):
    async def get_decimals(self, token_addr):
        return (await self.get(token_addr))['decimals']

    async def get_name(self, token_addr):
        return (await self.get(token_addr))['name']

    async def get_symbol(self, token_addr):
        return (await self.get(token_addr))['symbol']

    async def batch_process(self):
        if len(self.items) == 0:
            return
        self.items = list(set(self.items))
        # logger.info(f'token service - 1: items={len(self.items)}')
        calls = []
        for token in self.items:
            calls += [
                AsyncCall(token, ['decimals()(uint8)', ], [[f"{token}:decimals", None]]),
                AsyncCall(token, ['name()(string)', ], [[f"{token}:name", None]]),
                AsyncCall(token, ['symbol()(string)', ], [[f"{token}:symbol", None]]),
            ]
        # logger.info('decimals to cache: %s', len(calls))
        multi = AsyncMulticall(calls, _w3=async_bsc_web3)
        try:
            results = await multi()
        except BaseException as e:
            logger.debug('token service await multi(): %s', e, exc_info=e)
            logger.warning('token service await multi(): %s', e)
            return

        tokens = {}
        for key, val in results.items():
            token, name = key.split(":")
            tokens.setdefault(token, {})
            tokens[token][name] = val

        for token, val in tokens.items():
            self.rdb.set(token, val)

        logger.info(f'token service - 2: items={len(self.items)}')
        self.clear()


inst = TokenService()
