import asyncio
import logging
from asyncio import Queue
from asyncio.queues import QueueEmpty
from datetime import datetime
from typing import List

from web3 import Web3

from util.asyncio.cancelable import Cancelable
from util.multicall.async_multicall import AsyncMulticall, AsyncCall
from util.redis.redis_util import RedisUtil
from util.uniswap.trade import Trade
from util.web3.util import async_bsc_web3

RDB = RedisUtil()
logger = logging.getLogger(__name__)


class SyncHandler(Cancelable):
    def __init__(self, trade_queue: Queue, w3: Web3):
        self.w3 = w3
        self.trade_queue = trade_queue
        self.queue = Queue()

    def cache_get(self, key):
        return RDB.get('bsc:' + key)

    def cache_set(self, key, val):
        return RDB.set('bsc:' + key, val)

    async def run(self):
        max_secs = 10
        # max_trades = 100
        last_time = datetime.now()

        trades = []
        while self.is_running():
            if (datetime.now() - last_time).total_seconds() < max_secs:
                try:
                    trade = self.trade_queue.get_nowait()
                    trades.append(trade)
                except QueueEmpty:
                    await asyncio.sleep(0.1)
                    continue
            else:
                await self.handle_trades(trades)
                trades = []
                last_time = datetime.now()

    async def handle_trades(self, trades: List[Trade]):
        # logger.info('handle_trades')
        await self.cache_all_pairs(trades)
        await self.cache_all_decimals(trades)

        # 计算交易后价格
        for trade in trades:
            log_pairs = {}
            for log in trade.logs_sync:
                pair_addr = log['address'].lower()
                pair_info = self.cache_get(pair_addr)
                decimals0 = self.cache_get_decimals(pair_info['token0'])
                decimals1 = self.cache_get_decimals(pair_info['token1'])
                # if trade_pair.quote_token not in list(pair_info.values()):
                #     continue

                log_pair = trade.calc_price(log, pair_info['token0'], pair_info['token1'], decimals0=decimals0,
                                            decimals1=decimals1)
                if not log_pair:
                    continue
                # logger.info('trade log: %s', log_pair)
                log_pairs[log_pair.quote_token] = log_pair
                # break

            trade_pair = trade.to_sorted_pair()
            if not trade_pair:
                # 这个交易不是直接用 usdt/busd/bnb 来完成的
                # logger.warning('trade obj sort pair failed: %s', str(trade))
                continue

            if trade_pair.quote_token not in log_pairs:
                logger.warning('no quote found in log_pairs: txh=%s', trade.hash)
                continue
            trade.price_pair = log_pairs[trade_pair.quote_token]
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
                pair_info = self.cache_get(pair_addr)

                all_tokens.add(pair_info['token0'].lower())
                all_tokens.add(pair_info['token1'].lower())

        to_get_decimals = set()
        for token in all_tokens:
            if self.cache_get_decimals(token) is None:
                to_get_decimals.add(token)
                uncache_cnt += 1
            else:
                cache_cnt += 1

        # logger.info('decimals to cache: %s vs %s', uncache_cnt, cache_cnt)
        if len(to_get_decimals) > 0:
            calls = []
            for token in to_get_decimals:
                calls += [
                    AsyncCall(token, ['decimals()(uint8)', ], [[token, None]]),
                ]
            # logger.info('decimals to cache: %s', len(calls))
            multi = AsyncMulticall(calls, _w3=async_bsc_web3)
            results = await multi()
            for token, decimals in results.items():
                self.cache_set_decimals(token, decimals)

    async def cache_all_pairs(self, trades):
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
