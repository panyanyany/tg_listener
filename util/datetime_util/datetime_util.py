import logging
import sys
from datetime import datetime

import arrow
from dateutil.parser import parse
from dateutil.tz import tzlocal
from dateutil.utils import default_tzinfo
from pytz import timezone


def dtt_parse(dt_str, tz_name=None) -> datetime:
    if sys.platform == 'win32':
        tz_info = tzlocal()
    else:
        if tz_name:
            tz_info = timezone(tz_name)
        else:
            tz_info = tzlocal()

    if isinstance(dt_str, int):
        dt_str = datetime.fromtimestamp(dt_str)
    if isinstance(dt_str, datetime):
        return dt_str.replace(tzinfo=tz_info)
    return default_tzinfo(parse(dt_str), tz_info)
