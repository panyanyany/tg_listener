import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base = declarative_base()

def db_connect(mysql):
    session = sessionmaker()
    """
    inst.conn = pymysql.connect(host=mysql['host'],
                                 user=mysql['user'],
                                 password=mysql['password'],
                                 db=mysql['db_name'],
                                 charset=mysql['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)
                                 """
    
    db_url_tpl = "mysql://{user}:{password}@{host}/{db_name}?charset={charset}"
    db_url = db_url_tpl.format(user=mysql['USER'], 
                  password=mysql['PASSWORD'],
                  host=mysql['HOST'],
                  db_name=mysql['NAME'],
                  charset=mysql['OPTIONS']['charset'])
    engine = create_engine(db_url)
    session.configure(bind=engine)
    return session()

def mongo_connect():
    import pymongo
    client = pymongo.MongoClient("localhost", 27017)
    db = client.wechat
    return db

