from datetime import datetime

from arctic import Arctic, CHUNK_STORE
from arctic.chunkstore.chunkstore import ChunkStore
from arctic.store.version_store import VersionStore
from arctic.tickstore.tickstore import TickStore
from pymongo import MongoClient
from pymongo.collection import Collection


class ArcticRepo:
    def __init__(self):
        a = Arctic('localhost')

        lib_name = 'tg_listener_tick'
        a.initialize_library(lib_name, lib_type=CHUNK_STORE)
        self.db_tick: ChunkStore = a[lib_name]

        client = MongoClient()
        self.db_data = client['tg_listener_data']

        # lib_name = 'tg_listener.stat'
        # a.initialize_library(lib_name, lib_type=CHUNK_STORE)
        # self.db_tick: ChunkStore = a[lib_name]

    def add_liq(self, token: str, method: str, ticks, amount_in: dict):
        key = f'{token}:liq'
        self.db_tick.append(key, ticks, upsert=True)
        self.update_stat_pool(token, method, amount_in)
        # self.update_stat(token, datetime.now())

    def add_ticks(self, token, ticks):
        key = f'{token}:tick'
        self.db_tick.append(key, ticks, upsert=True)
        self.update_stat(token, datetime.now())

    def add_buy(self, token, ticks):
        self.db_tick.append(f'{token}:buy', ticks, upsert=True)

    def add_sell(self, token, ticks):
        self.db_tick.append(f'{token}:sell', ticks, upsert=True)

    def update_stat_pool(self, token, method, amount_in):
        stat = self.update_stat(token)
        sign = 1
        if method == 'remove':
            sign = -1

        stat.setdefault('pools', {})
        for name, amt in amount_in.items():
            stat['pools'].setdefault(name, 0)
            stat['pools'][name] += sign * amt

        self.update_stat(token, pools=stat['pools'])

    def get_stat(self, token):
        stats: Collection = self.db_data.stats
        cond = {"token": token}
        stat = stats.find_one(cond)
        return stat

    def update_stat(self, token, last_tick_at=None, pools=None, is_dividend=False, name=None, symbol=None):
        stats: Collection = self.db_data.stats
        cond = {"token": token}
        stat = stats.find_one(cond)
        if not stat:
            stat = {"token": token, "recorded_at": datetime.now(), "pools": {}}
            stats.insert_one(stat)
        if last_tick_at:
            stat['last_tick_at'] = last_tick_at
        if pools:
            stat.setdefault('pools', {})
            stat['pools'].update(pools)
        if is_dividend:
            stat['is_dividend'] = is_dividend
        if name:
            stat['name'] = name
        if symbol:
            stat['symbol'] = symbol
        stats.update_one(cond, {"$set": stat})
        return stat


arctic_db = ArcticRepo()
