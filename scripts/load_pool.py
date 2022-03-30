import json

import arrow

from tg_listener.db import init_database
from tg_listener.models.AddressStat import AddressStat
from util.sys_util import myexec

init_database()


def getPair(addr):
    out, err = myexec("bin/hunt psPair " + addr,
                      cwd="/var/www/pyys/tugou-hunter")
    if err or out == '':
        print(err)
        return None

    jd = json.loads(out)
    return jd


def main():
    today = arrow.now().date()
    query = AddressStat.select().where(
        (AddressStat.created_at.year == today.year) &
        (AddressStat.created_at.month == today.month) &
        (AddressStat.created_at.day == today.day))

    pairs = []
    for md in query:
        md: AddressStat
        # if md.busd_amount:
        #     continue
        pairs.append(md.address)

    if len(pairs) == 0:
        return
    print('querying pairs', ','.join(pairs))
    all_pair_info = getPair(','.join(pairs))

    for md in query:
        md: AddressStat
        # if md.busd_amount:
        #     continue
        # if md.address != '0x552594612f935441c01c6854edf111f343c1ca07':
        #     continue

        if md.address not in all_pair_info:
            print('not found pair', md.address)
            continue
        jd = all_pair_info[md.address]
        busd_amount = jd['totalBusdAmount']
        busd_amount = busd_amount / (10 ** 12)

        if not md.init_busd_amount:
            md.init_busd_amount = busd_amount
        md.now_busd_amount = busd_amount
        if md.now_busd_amount == 0:
            md.pool_growth = -1
        else:
            md.pool_growth = (md.now_busd_amount - md.init_busd_amount) / md.init_busd_amount
        md.symbol = jd['tokenQuote']['symbol'][:255]
        md.name = jd['tokenQuote']['name'][:255]
        md.save()

        print(md.symbol, busd_amount)


main()
