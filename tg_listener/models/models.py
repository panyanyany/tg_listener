import datetime

import arrow
from peewee import Model, DateTimeField, Proxy, CharField, IntegerField

database_proxy = Proxy()


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now, null=True)
    updated_at = DateTimeField(null=True)

    class Meta:
        database = database_proxy
        # 自动生成以下划线分隔的表名
        # @see http://docs.peewee-orm.com/en/latest/peewee/models.html#table-names
        legacy_table_names = False
        table_settings = ['DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin']

    def save(self, *args, update=True, **kwargs):
        if update and hasattr(self, 'updated_at'):
            self.updated_at = arrow.now().datetime
        return super().save(*args, **kwargs)

    @classmethod
    def get_new_values(cls, field, values):
        existed_subs = [getattr(md, field) for md in cls.select().where(getattr(cls, field).in_(values))]
        new_subs = list(set(values) - set(existed_subs))
        return new_subs


class AddressRecord(BaseModel):
    address = CharField()
    text = CharField(max_length=1024)
    chat_name = CharField()
    chat_id = IntegerField()
    user_fullname = CharField(null=True)
    user_id = IntegerField()
    username = CharField(null=True)


