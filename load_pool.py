import json

import arrow

from tg_listener.db import init_database
from tg_listener.models import AddressStat
from util.sys_util import myexec

init_database()


def getPair(addr):
    out, err = myexec("bin/hunt psPair " + addr,
                      cwd="/var/www/pyys/tugou-hunter")
    if err or out == '':
        return None

    jd = json.loads(out)
    return jd


def main():
    today = arrow.now().date()
    query = AddressStat.select().where(
        (AddressStat.created_at.year == today.year) &
        (AddressStat.created_at.month == today.month) &
        (AddressStat.created_at.day == today.day))

    for md in query:
        md: AddressStat
        if md.busd_amount:
            continue
        # if md.address != '0x552594612f935441c01c6854edf111f343c1ca07':
        #     continue

        jd = getPair(md.address)
        if not jd:
            continue
        jd = jd[md.address]
        busd_amount = jd['totalBusdAmount']
        busd_amount = busd_amount / (10 ** 12)

        md.busd_amount = busd_amount
        md.symbol = jd['tokenQuote']['symbol'][:255]
        md.save()

        print(md.symbol, busd_amount)


main()
