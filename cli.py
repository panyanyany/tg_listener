import logging

from tg_listener.db import init_database
from tg_listener.models.AddressStat import make_stat
from tg_listener.repo.tg_listener_repo import Listener

db = init_database()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

make_stat()

Listener().run()
