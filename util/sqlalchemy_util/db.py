import pymysql
pymysql.install_as_MySQLdb()
import time

from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# engine = init_engine(global_settings.DATABASES)
def new_session(engine, interval=3):
    DB_Session = sessionmaker()
    # session = DB_Session(bind=self.engine)
    DB_Session.configure(bind=engine)
    while True:
        try:
            engine.execute('select 1')
            break
        except Exception as e:
            print(e)
        time.sleep(interval)
    return DB_Session()


def init_engine(db_cfg):
    # dbs = global_settings.DATABASES
    mysql = db_cfg
    
    db_url_tpl = "mysql://{user}:{password}@{host}/{db_name}?charset={charset}"
    db_url = db_url_tpl.format(user=mysql['USER'], 
                  password=mysql['PASSWORD'],
                  host=mysql['HOST'],
                  db_name=mysql['NAME'],
                  charset=mysql['OPTIONS']['charset'])
    engine = create_engine(db_url)
    return engine
