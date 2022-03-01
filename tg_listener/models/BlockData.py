import arrow
from peewee import CharField, IntegerField, DateField, DecimalField

import settings

from tg_listener.models.models import BaseModel, AddressRecord


class BlockData(BaseModel):
    hash = CharField(max_length=1024)
    number = IntegerField()
    timestamp = IntegerField()
