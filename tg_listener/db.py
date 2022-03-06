import logging
import asyncio
import threading

from playhouse.pool import PooledMySQLDatabase
from playhouse.db_url import connect, MySQLDatabase
from playhouse.migrate import MySQLMigrator, migrate, CharField, IntegerField, DecimalField

import settings
from tg_listener.models.models import database_proxy, AddressRecord
from tg_listener.models.AddressStat import AddressStat

db_inst: MySQLDatabase = None


def keep_alive():
    # mysql 的连接只能保持 8 小时，之后会断开，用这个方法保活
    async def ping():
        while True:
            await asyncio.sleep(60)
            result = db_inst.execute_sql('select 1')
            print('ping result:', result)

    asyncio.run(ping())


def init_database():
    global db_inst
    # db_inst = connect('mysql://{username}:{password}@127.0.0.1:3306/{db_name}'.format(
    #     username=settings.DB_USERNAME,
    #     password=settings.DB_PASSWORD,
    #     db_name=settings.DB_NAME,
    # ), charset='utf8mb4')
    # 为什么要用 PooledMySQLDatabase 呢？
    # 因为 mysql 的连接总是会自动断开，不管你有没有 ping, pool 会自动回收处理无效的连接
    db_inst = PooledMySQLDatabase(settings.DB_NAME, user=settings.DB_USERNAME, password=settings.DB_PASSWORD,
                                  charset='utf8mb4')

    database_proxy.initialize(db_inst)

    db_inst.connect()
    db_inst.execute_sql("SET collation_connection = 'utf8mb4_bin';")
    # self.db.drop_tables([VideoTask])  # debug
    # db.drop_tables(
    #     [RecognizeRecord, SearchResult, SearchTask, CrawlPageTask, ExtractTask, PersonResume,
    #      EnPeopleCrawlTask, EnDomainScanTask, EnUrlScanTask])
    # db.drop_tables([
    #     EnIntroUrlScanTask,
    # ])
    db_inst.create_tables(
        [AddressRecord, AddressStat])

    migrator = MySQLMigrator(db_inst)

    add_columns = [
        # ['address_stat', 'now_busd_amount', IntegerField(null=True)],
        # ['address_stat', 'pool_growth', DecimalField(null=True)],
    ]
    rename_columns = [
        # ['address_stat', 'busd_amount', 'init_busd_amount'],
    ]

    alter_columns = [
        # ['address_stat', 'name', CharField(null=True)],
        # ['file_node', 'outer_id', CharField(unique=False)],
        # ['article_task', 'new_img_urls', CharField(max_length=4096, default='', null=True)],
    ]

    try:
        migrate(
            # migrator.add_index('account_info', ('username', 'mp'), unique=True),
            # migrator.drop_index('account_info', 'account_info_username_mp'),
        )
    except Exception as e:
        logging.debug('add_index: %s', str(e))

    for add_column_args in add_columns:
        try:
            migrate(
                migrator.add_column(*add_column_args),
            )
        except Exception as e:
            logging.warning('!!!! add_column: %s', str(e))

    for rename_column_args in rename_columns:
        try:
            migrate(
                migrator.rename_column(*rename_column_args),
            )
        except Exception as e:
            logging.warning('!!!! rename_column: %s', str(e))

    for alter_column_args in alter_columns:
        try:
            migrate(
                migrator.alter_column_type(*alter_column_args),
            )
        except Exception as e:
            logging.warning('!!!! alter_column_type: %s', str(e))

    # threading.Thread(target=keep_alive, daemon=True).start()
    return db_inst
