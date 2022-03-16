from arctic import Arctic, CHUNK_STORE
from arctic.chunkstore.chunkstore import ChunkStore
from arctic.store.version_store import VersionStore
from arctic.tickstore.tickstore import TickStore


class ArcticRepo:
    def __init__(self):
        lib_name = 'tg_listener'
        a = Arctic('localhost')
        # a.initialize_library(lib_name)
        a.initialize_library(lib_name, lib_type=CHUNK_STORE)

        self.lib: ChunkStore = a[lib_name]

    def add_ticks(self, token, ticks):
        key = f'{token}_tick'
        self.lib.write(key, ticks)

    def add_buy(self, token, ticks):
        self.lib.append(f'{token}:buy', ticks, upsert=True)

    def add_sell(self, token, ticks):
        self.lib.append(f'{token}:sell', ticks, upsert=True)


arctic_db = ArcticRepo()
