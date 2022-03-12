import asyncio
import logging
from asyncio import Queue
from asyncio.queues import QueueEmpty
from datetime import datetime
from typing import List

from multicall import Multicall, Call
from multicall.constants import MULTICALL2_ADDRESSES, MULTICALL2_BYTECODE
from multicall.multicall import get_multicall_map
from web3 import Web3

from util.asyncio.cancelable import Cancelable
from util.redis.redis_util import RedisUtil
from util.uniswap.trade import Trade
from util.web3.util import bsc_web3

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
        max_secs = 20
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
        self.cache_all_pairs(trades)
        self.cache_all_decimals(trades)

    def cache_all_decimals(self, trades):
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
            key = 'decimals:' + token
            if self.cache_get(key) is None:
                to_get_decimals.add(token)
                uncache_cnt += 1
            else:
                cache_cnt += 1

        logger.info('decimals to cache: %s vs %s', uncache_cnt, cache_cnt)
        if len(to_get_decimals) > 0:
            calls = []
            for token in to_get_decimals:
                calls += [
                    Call(token, ['decimals()(uint8)', ], [[token, None]]),
                ]
            # logger.info('decimals to cache: %s', len(calls))
            multi = Multicall(calls, _w3=bsc_web3)
            results = multi()
            for token, decimals in results.items():
                key = 'decimals:' + token
                self.cache_set(key, decimals)

    def cache_all_pairs(self, trades):
        # 缓存所有 lp 信息
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

        logger.info('pairs to cache: %s vs %s', uncache_cnt, cache_cnt)
        if len(all_pair_addrs) > 0:
            calls = []
            for pair_addr in all_pair_addrs:
                calls += [
                    Call(pair_addr, ['token0()(address)', ], [[pair_addr + ':token0', None]]),
                    Call(pair_addr, ['token1()(address)', ], [[pair_addr + ':token1', None]]),
                ]

            multi = Multicall(calls, _w3=bsc_web3)
            results = multi()
            all_pairs = {}
            for key, val in results.items():
                pair_addr, token_name = key.split(':')
                pair_info = all_pairs.get(pair_addr, {})
                pair_info[token_name] = val

                all_pairs[pair_addr] = pair_info

            for pair_addr, info in all_pairs.items():
                self.cache_set(pair_addr, info)
