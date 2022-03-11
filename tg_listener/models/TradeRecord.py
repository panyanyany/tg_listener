import arrow
from peewee import CharField, IntegerField, DateField, DecimalField

import settings

from tg_listener.models.models import BaseModel, AddressRecord


class TradeRecord(BaseModel):
    token_address = CharField()
    from_address = CharField()
    to_address = CharField()
    direction = CharField()

    amount = CharField()
    usdt_amount = DecimalField()

    D_BUY = 'BUY'
    D_SELL = 'SELL'

    class Meta:
        indexes = (
            (('address', 'day'), True),
        )
