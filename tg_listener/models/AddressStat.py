import arrow
from peewee import CharField, IntegerField, DateField

import settings

from tg_listener.models.models import BaseModel, AddressRecord


class AddressStat(BaseModel):
    address = CharField()
    cnt = IntegerField()
    memo = CharField(null=True)
    symbol = CharField(null=True)
    name = CharField(null=True)
    init_busd_amount = IntegerField(null=True)
    now_busd_amount = IntegerField(null=True)
    day = DateField()

    class Meta:
        indexes = (
            (('address', 'day'), True),
        )


def make_stat():
    today = arrow.now().date()
    # 加载 record
    query = AddressRecord.select().where(
        (AddressRecord.created_at.year == today.year) &
        (AddressRecord.created_at.month == today.month) &
        (AddressRecord.created_at.day == today.day))

    # 统计 addr-user
    stat1 = {}
    for md in query:
        md: AddressRecord
        addr = md.address.lower()
        if addr in settings.BLOCK_ADDRESSES:
            continue

        key = (addr, md.user_id)
        stat1.setdefault(key, 0)
        stat1[key] += 1

    # 统计 addr
    stat2 = {}
    for key, cnt in stat1.items():
        addr = key[0]
        stat2.setdefault(addr, 0)
        stat2[addr] += 1

    today_str = today.today().strftime('%Y-%m-%d')
    query = AddressStat.select().where(AddressStat.day == today_str)
    exists_stat = {}
    for md in query:
        md: AddressStat
        exists_stat[md.address] = md

    to_update_stat = []
    to_insert_stat = []
    for addr, cnt in stat2.items():
        if addr in exists_stat:
            md = exists_stat[addr]
            md: AddressStat

            md.cnt = cnt
            md.updated_at = arrow.now().datetime
            to_update_stat.append(md)
        else:
            md: AddressStat = AddressStat()
            md.address = addr
            md.cnt = cnt
            md.day = today_str
            md.created_at = arrow.now().datetime
            to_insert_stat.append(md)

    print(arrow.now(),
          'insert: {insert}, update: {update}'.format(insert=len(to_insert_stat), update=len(to_update_stat)))
    # AddressStat.insert_many(items).on_conflict(preserve=[AddressStat.cnt], update={}).execute()

    AddressStat.bulk_update(to_update_stat, fields=['cnt', 'updated_at'], batch_size=50)
    AddressStat.bulk_create(to_insert_stat, batch_size=50)
