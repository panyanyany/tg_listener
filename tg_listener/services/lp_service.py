import logging
from asyncio import QueueEmpty

from tg_listener.services import base_service
from util.multicall.async_multicall import AsyncCall, AsyncMulticall
from util.web3.util import async_bsc_web3

logger = logging.getLogger(__name__)


class LpService(base_service.BaseService):

    async def batch_process(self):
        if len(self.items) == 0:
            return
        self.items = list(set(self.items))
        # logger.info(f'lp service - 1: items={len(self.items)}')
        calls = []
        for pair_addr in self.items:
            calls += [
                AsyncCall(pair_addr, ['token0()(address)', ], [[pair_addr + ':token0', None]]),
                AsyncCall(pair_addr, ['token1()(address)', ], [[pair_addr + ':token1', None]]),
            ]

        multi = AsyncMulticall(calls, _w3=async_bsc_web3)
        try:
            results = await multi()
        except BaseException as e:
            logger.debug('lp service await multi(): %s', e, exc_info=e)
            logger.warning('lp service await multi(): %s', e)
            return
        all_pairs = {}
        for key, val in results.items():
            pair_addr, token_name = key.split(':')
            pair_info = all_pairs.get(pair_addr, {})
            pair_info[token_name] = val

            all_pairs[pair_addr] = pair_info

        for pair_addr, info in all_pairs.items():
            if not info['token0'] or not info['token1']:
                logger.error("lp token0 or token1 is None: lp=%s, info=%s", pair_addr, info)
                continue
            info['token0'] = info['token0'].lower()
            info['token1'] = info['token1'].lower()
            self.rdb.set(pair_addr, info)

        logger.info(f'lp service - 2: items={len(self.items)}')
        self.clear()


inst = LpService()
