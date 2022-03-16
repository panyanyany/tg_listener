from arctic import Arctic
from arctic.store.version_store import VersionStore
from arctic.tickstore.tickstore import TickStore


class ArcticRepo:
    def __init__(self):
        lib_name = 'tg_listener'
        a = Arctic('localhost')
        a.initialize_library(lib_name)
        self.lib: VersionStore = a[lib_name]

    def add_ticks(self, token, ticks):
        self.lib.append(f'{token}:tick', ticks)

    def add_buy(self, token, ticks):
        self.lib.append(f'{token}:buy', ticks)

    def add_sell(self, token, ticks):
        self.lib.append(f'{token}:sell', ticks)


arctic_db = ArcticRepo()
