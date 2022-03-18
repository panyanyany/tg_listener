import asyncio
import logging
from asyncio import Queue
from asyncio.queues import QueueEmpty
from datetime import datetime
from typing import List

from requests import ReadTimeout
from web3 import Web3

from tg_listener.services import lp_service, token_service
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
        self.bnb_price = 0
        self.cake_price = 0

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
        self.get_bnb_price()
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

            if (datetime.now() - last_time_get_price).total_seconds() > max_secs_get_price:
                try:
                    self.get_bnb_price()
                    last_time_get_price = datetime.now()
                except ReadTimeout as e:
                    pass
                except BaseException as e:
                    logger.error('get bnb price', exc_info=e)

    def get_bnb_price(self):
        self.bnb_price = Multicall(web3=bsc_web3).get_bnb_price() / (10 ** 12)
        logger.info('bnb price: %s', self.bnb_price)
        pair_info = Multicall(web3=bsc_web3).get_pair_info_with_price(cake_busd_pair)
        self.cake_price = pair_info.token_0.busd_price_human
        logger.info('cake price: %s', self.cake_price)

    async def handle_trade(self, trade: Trade):
        log_pairs = {}
        for log in trade.logs_sync:
            pair_addr = log['address'].lower()

            ts = datetime.now()
            pair_info = await lp_service.inst.get(pair_addr)
            diff = (datetime.now() - ts).total_seconds()
            logger.debug(f'get pair_info, diff={diff}')

            ts = datetime.now()
            decimals0 = await token_service.inst.get(pair_info['token0'].lower())
            diff = (datetime.now() - ts).total_seconds()
            logger.debug(f'get decimals0, diff={diff}')

            ts = datetime.now()
            decimals1 = await token_service.inst.get(pair_info['token1'].lower())
            diff = (datetime.now() - ts).total_seconds()
            logger.debug(f'get decimals1, diff={diff}')
            # if trade_pair.quote_token not in list(pair_info.values()):
            #     continue

            log_pair = trade.calc_price(log, pair_info['token0'], pair_info['token1'], decimals0=decimals0,
                                        decimals1=decimals1)
            if not log_pair:
                continue
            if 'usd' not in log_pair.price_in:
                if 'bnb' in log_pair.price_in:
                    log_pair.price_in['usd'] = log_pair.price_in['bnb'] * self.bnb_price
                elif 'cake' in log_pair.price_in:
                    log_pair.price_in['usd'] = log_pair.price_in['cake'] * self.cake_price
            # logger.info('trade log: %s', log_pair)
            # print(log_pair)
            log_pairs[log_pair.quote_token] = log_pair
            # break

        trade_pair = trade.to_sorted_pair()
        if not trade_pair:
            # 这个交易不是直接用 usdt/busd/bnb 来完成的
            # logger.warning('trade obj sort pair failed: %s', str(trade))
            return trade

        if trade_pair.quote_token not in log_pairs:
            logger.warning('no quote found in log_pairs: txh=%s', trade.hash)
            return trade
        trade.price_pair = log_pairs[trade_pair.quote_token]
        return trade

    async def handle_trades(self, trades: List[Trade]):
        if len(trades) == 0:
            return
        logger.info(f'handle_trades - 1: trades={len(trades)}')
        await self.cache_all_pairs(trades)
        await self.cache_all_decimals(trades)
        logger.info(f'handle_trades - 2: trades={len(trades)}')

        # 计算交易后价格
        price_trades = []
        for trade in trades:
            trade = await self.handle_trade(trade)
            if not trade.price_pair:
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
        all_tokens = set()
        cache_cnt = 0
        uncache_cnt = 0

        for trade in trades:
            for log in trade.logs_sync:
                pair_addr = log['address'].lower()
                pair_info = await lp_service.inst.get(pair_addr)

                all_tokens.add(pair_info['token0'].lower())
                all_tokens.add(pair_info['token1'].lower())

        for token in all_tokens:
            token_service.inst.add(token)

    async def cache_all_pairs(self, trades):
        """ 缓存所有 lp 信息 """
        for trade in trades:
            for log in trade.logs_sync:
                pair_addr = log['address'].lower()
                lp_service.inst.add(pair_addr)

    async def cache_all_pairs2(self, trades):
        """ 缓存所有 lp 信息 """
        all_pair_addrs = set()
        cache_cnt = 0
        uncache_cnt = 0
        for trade in trades:
            for log in trade.logs_sync:
                pair_addr = log['address'].lower()
                if self.cache_get(pair_addr) is None:
                    all_pair_addrs.add(pair_addr)
                    uncache_cnt += 1
                else:
                    cache_cnt += 1

        # logger.info('pairs to cache: %s vs %s', uncache_cnt, cache_cnt)
        if len(all_pair_addrs) > 0:
            calls = []
            for pair_addr in all_pair_addrs:
                calls += [
                    AsyncCall(pair_addr, ['token0()(address)', ], [[pair_addr + ':token0', None]]),
                    AsyncCall(pair_addr, ['token1()(address)', ], [[pair_addr + ':token1', None]]),
                ]

            multi = AsyncMulticall(calls, _w3=async_bsc_web3)
            results = await multi()
            all_pairs = {}
            for key, val in results.items():
                pair_addr, token_name = key.split(':')
                pair_info = all_pairs.get(pair_addr, {})
                pair_info[token_name] = val

                all_pairs[pair_addr] = pair_info

            for pair_addr, info in all_pairs.items():
                info['token0'] = info['token0'].lower()
                info['token1'] = info['token1'].lower()
                self.cache_set(pair_addr, info)
