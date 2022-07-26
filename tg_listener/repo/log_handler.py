import asyncio
import logging
from asyncio import Queue
from asyncio.queues import QueueEmpty
from datetime import datetime
from typing import List

from requests import ReadTimeout
from web3 import Web3

from tg_listener.services import lp_service, token_service, price_service
from util.asyncio.cancelable import Cancelable
from util.bsc.constants import cake_busd_pair
from util.bsc.pancake_swap.multicall import Multicall
from util.multicall.async_multicall import AsyncMulticall, AsyncCall
from util.redis.redis_util import RedisUtil
from util.uniswap.trade import Trade
from util.web3.util import async_bsc_web3, bsc_web3

RDB = RedisUtil()
logger = logging.getLogger(__name__)


class SyncHandler(Cancelable):
    """通过 Sync 日志来计算交易后价格"""

    def __init__(self, trades_queue: Queue, w3: Web3):
        self.w3 = w3
        self.trades_queue = trades_queue
        self.price_trades_queue = Queue()

    def cache_get(self, key):
        return RDB.get('bsc:' + key)

    def cache_set(self, key, val):
        return RDB.set('bsc:' + key, val)

    async def run(self):
        max_secs = 5
        max_secs_get_price = 60

        last_time = datetime.now()
        last_time_get_price = datetime.now()

        trades = []
        # self.get_bnb_price()
        while self.is_running():
            if (datetime.now() - last_time).total_seconds() < max_secs:
                # 拿队列
                try:
                    trades += self.trades_queue.get_nowait()
                except QueueEmpty:
                    await asyncio.sleep(0.1)
                    continue
            else:
                try:
                    # 处理交易
                    await self.handle_trades(trades)
                    trades = []
                    last_time = datetime.now()
                except BaseException as e:
                    logger.debug('error detail', exc_info=e)
                    logger.error('handle_trades: %s', e)
                    if 'no running event loop' in str(e):
                        raise
                    # 暂停一下，免得无法 Ctrl-C
                    await asyncio.sleep(1)

    async def handle_swap(self, trade: Trade):
        trade_pair = trade.to_sorted_pair()
        if not trade_pair:
            # 这个交易不是直接用 usdt/busd/bnb 来完成的
            # logger.warning('trade obj sort pair failed: %s', str(trade))
            return trade

        swap_pairs = {}
        for log in trade.logs_swap:
            pair_addr = log['address'].lower()

            try:
                pair_info = await lp_service.inst.get(pair_addr)
                decimals0 = await token_service.inst.get_decimals(pair_info['token0'].lower())
                decimals1 = await token_service.inst.get_decimals(pair_info['token1'].lower())
            except TimeoutError as e:
                logger.warning('service call failed: %s', e)
                continue
            if decimals0 is None:
                logger.error("decimals0 is None, token0=%s", pair_info['token0'].lower())
                continue
            if decimals1 is None:
                logger.error("decimals1 is None, token1=%s", pair_info['token1'].lower())
                continue

            # print(log)
            # 0x327a7a75e0f372847209878650d59078a1fc14ba6baa5003e5d8b3c2e745bd86
            # 同时有 amount0In, amount1In, amount0Out
            # 0x6842abd55496d13c33302a95f57b6e1801e7c6e4daff8ac977d272aa4e5d9de6
            amount0 = log['args']['amount0Out']
            if amount0 == 0:
                amount0 = log['args']['amount0In']
            log_pair = trade.calc_price(log, pair_info['token0'], pair_info['token1'],
                                        amount0=amount0,
                                        amount1=log['args']['amount1In'] + log['args']['amount1Out'],
                                        decimals0=decimals0,
                                        decimals1=decimals1,
                                        bnb_price=await price_service.inst.get_bnb_price(),
                                        cake_price=await price_service.inst.get_cake_price())
            if not log_pair:
                continue
            # logger.info('trade log: %s', log_pair)
            # print(log_pair)
            log_pair.lp = pair_addr
            if log_pair.quote_token not in swap_pairs:
                swap_pairs[log_pair.quote_token] = log_pair
            else:
                if swap_pairs[log_pair.quote_token].quote_res < log_pair.quote_res:
                    swap_pairs[log_pair.quote_token] = log_pair
            # break

        if trade_pair.quote_token not in swap_pairs:
            logger.debug('no quote found in swap_pairs: txh=%s', trade.hash)
            return trade
        trade.price_pair = swap_pairs[trade_pair.quote_token]
        return trade

    async def handle_sync(self, trade: Trade):
        log_pairs = {}
        for log in trade.logs_sync:
            pair_addr = log['address'].lower()

            try:
                pair_info = await lp_service.inst.get(pair_addr)
                decimals0 = await token_service.inst.get_decimals(pair_info['token0'].lower())
                decimals1 = await token_service.inst.get_decimals(pair_info['token1'].lower())
            except TimeoutError as e:
                logger.warning(e)
                continue
            if decimals0 is None:
                logger.error("decimals0 is None, token0=%s", pair_info['token0'].lower())
                continue
            if decimals1 is None:
                logger.error("decimals1 is None, token1=%s", pair_info['token1'].lower())
                continue

            log_pair = trade.calc_price(log, pair_info['token0'], pair_info['token1'], decimals0=decimals0,
                                        decimals1=decimals1,
                                        amount0=log['args']['reserve0'],
                                        amount1=log['args']['reserve1'],
                                        bnb_price=await price_service.inst.get_bnb_price(),
                                        cake_price=await price_service.inst.get_cake_price())
            if not log_pair:
                continue
            # logger.info('trade log: %s', log_pair)
            # print(log_pair)
            log_pair.lp = pair_addr
            log_pairs[log_pair.quote_token] = log_pair
            # break

        trade_pair = trade.to_sorted_pair()
        if not trade_pair:
            # 这个交易不是直接用 usdt/busd/bnb 来完成的
            # logger.warning('trade obj sort pair failed: %s', str(trade))
            return trade

        if trade_pair.quote_token not in log_pairs:
            logger.debug('no quote found in log_pairs: txh=%s', trade.hash)
            return trade
        trade.res_pair = log_pairs[trade_pair.quote_token]
        return trade

    async def handle_trades(self, trades: List[Trade]):
        if len(trades) == 0:
            return
        # logger.info(f'handle_trades - 1: trades={len(trades)}')
        await self.cache_all_pairs(trades)
        await self.cache_all_decimals(trades)
        # logger.info(f'handle_trades - 2: trades={len(trades)}')

        # 计算交易后价格
        price_trades = []
        for trade in trades:
            trade = await self.handle_swap(trade)
            if not trade.price_pair:
                continue
            trade = await self.handle_sync(trade)
            if not trade.res_pair:
                continue
            price_trades.append(trade)
        logger.info(f'handle_trades - 3: price_trades={len(price_trades)}')
        self.price_trades_queue.put_nowait(price_trades)
        price_trades = []
        # logger.info('trade: %s', trade.price_pair)

    def cache_get_decimals(self, token):
        key = 'decimals:' + token
        return self.cache_get(key)

    def cache_set_decimals(self, token, val):
        key = 'decimals:' + token
        return self.cache_set(key, val)

    async def cache_all_decimals(self, trades):
        """ 缓存所有代币的 decimals """
        for trade in trades:
            for log in trade.logs_swap:
                pair_addr = log['address'].lower()
                try:
                    pair_info = await lp_service.inst.get(pair_addr)
                except TimeoutError as e:
                    logger.warning(e)
                    continue

                token_service.inst.add(pair_info['token0'].lower())
                token_service.inst.add(pair_info['token1'].lower())

    async def cache_all_decimals0(self, trades):
        """ 缓存所有代币的 decimals """
        for trade in trades:
            for log in trade.logs_sync:
                pair_addr = log['address'].lower()
                try:
                    pair_info = await lp_service.inst.get(pair_addr)
                except TimeoutError as e:
                    logger.warning(e)
                    continue

                token_service.inst.add(pair_info['token0'].lower())
                token_service.inst.add(pair_info['token1'].lower())

    async def cache_all_pairs(self, trades):
        """ 缓存所有 lp 信息 """
        for trade in trades:
            for log in trade.logs_swap:
                pair_addr = log['address'].lower()
                lp_service.inst.add(pair_addr)

    async def cache_all_pairs0(self, trades):
        """ 缓存所有 lp 信息 """
        for trade in trades:
            for log in trade.logs_sync:
                pair_addr = log['address'].lower()
                lp_service.inst.add(pair_addr)
