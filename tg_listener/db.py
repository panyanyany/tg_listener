import logging

from playhouse.db_url import connect
from playhouse.migrate import MySQLMigrator, migrate

import settings
from tg_listener.models import database_proxy, AddressRecord, AddressStat


def init_database():
    db = connect('mysql://{username}:{password}@127.0.0.1:3306/{db_name}'.format(
        username=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
        db_name=settings.DB_NAME,
    ), charset='utf8mb4')
    database_proxy.initialize(db)

    db.connect()
    db.execute_sql("SET collation_connection = 'utf8mb4_bin';")
    # self.db.drop_tables([VideoTask])  # debug
    # db.drop_tables(
    #     [RecognizeRecord, SearchResult, SearchTask, CrawlPageTask, ExtractTask, PersonResume,
    #      EnPeopleCrawlTask, EnDomainScanTask, EnUrlScanTask])
    # db.drop_tables([
    #     EnIntroUrlScanTask,
    # ])
    db.create_tables(
        [AddressRecord, AddressStat])

    migrator = MySQLMigrator(db)

    add_columns = [
    ]

    alter_columns = [
        # ['crawl_page_tasks', 'url', CharField(null=True)],
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

    for alter_column_args in alter_columns:
        try:
            migrate(
                migrator.alter_column_type(*alter_column_args),
            )
        except Exception as e:
            logging.warning('!!!! alter_column_type: %s', str(e))
