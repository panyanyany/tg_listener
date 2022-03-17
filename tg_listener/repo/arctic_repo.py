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

    def add_ticks(self, token, ticks):
        key = f'{token}:tick'
        self.db_tick.append(key, ticks, upsert=True)
        self.update_stat(token, datetime.now())

    def add_buy(self, token, ticks):
        self.db_tick.append(f'{token}:buy', ticks, upsert=True)

    def add_sell(self, token, ticks):
        self.db_tick.append(f'{token}:sell', ticks, upsert=True)

    def update_stat(self, token, last_tick_at=None, pool=None):
        stats: Collection = self.db_data.stats
        cond = {"token": token}
        stat = stats.find_one(cond)
        if not stat:
            stat = {"token": token, "recorded_at": datetime.now()}
            stats.insert_one(stat)
        if last_tick_at:
            stat['last_tick_at'] = last_tick_at
        if pool:
            stat.setdefault('pools', {})
            stat['pools'].update(pool)
        stats.update_one(cond, {"$set": stat})


arctic_db = ArcticRepo()
