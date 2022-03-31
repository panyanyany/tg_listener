import logging

import arrow
from pyairtable import Table

import settings
from tg_listener.db import init_database
from tg_listener.models.AddressStat import AddressStat
from util.log_util import setup3, default_ignore_names

setup3(ignore_names=list(set(['web3.*', 'asyncio'] + default_ignore_names) - {'util.*'}), rm_parents=1)
init_database()

table = Table(settings.airtable['api_key'], 'appRLf4sYiFHWsI1D', '当天统计')
logger = logging.getLogger(__name__)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def load_stat():
    today = arrow.now().date()
    query = AddressStat.select().where(
        (AddressStat.created_at.year == today.year) &
        (AddressStat.created_at.month == today.month) &
        (AddressStat.created_at.day == today.day)).order_by(AddressStat.cnt.desc(),
                                                            AddressStat.init_busd_amount.desc()).limit(100)

    logger.debug('get %s AddressStat', len(query))
    stat = {}
    records = []
    for md in query:
        md: AddressStat
        if not md.symbol:
            stat.setdefault('no_symbol', 0)
            stat['no_symbol'] += 1
            continue
        if md.now_busd_amount <= 100:
            stat.setdefault('low_busd_amount', 0)
            stat['low_busd_amount'] += 1
            continue
        records.append({
            '代币符号': md.symbol,
            '代币名': md.name,
            '地址': md.address,
            '初始池': md.init_busd_amount or 0,
            '当前池': md.now_busd_amount or 0,
            '池涨幅': float(md.pool_growth),
            '推荐次数': md.cnt,
            '更新时间': str(md.updated_at),
        })

    logger.debug('%s records need to update, stat=%s', len(records), stat)
    ids = list(map(lambda e: e['id'], table.all()))
    if len(ids) > 0:
        for _ids in chunks(ids, 10):
            table.batch_delete(_ids)

    for _recs in chunks(records, 10):
        table.batch_create(_recs)


load_stat()
