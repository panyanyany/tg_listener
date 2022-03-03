import json
import logging
from datetime import timedelta

import arrow

from tg_listener.db import init_database
from tg_listener.models.AddressStat import AddressStat
from tg_listener.models.models import AddressRecord
from util.log_util import setup3
from util.sys_util import myexec

setup3()

init_database()

today = arrow.now().date()
max_age = arrow.now().shift(days=-6).datetime.replace(hour=0, minute=0, second=0, microsecond=0)

query = AddressStat.delete().where(AddressStat.created_at < max_age)
cnt = query.execute()
logging.info("deleted %s AddressStat", cnt)

query = AddressRecord.delete().where(AddressRecord.created_at < max_age)
cnt = query.execute()
logging.info("deleted %s AddressRecord", cnt)
