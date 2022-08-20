# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from DB.createDB import Connect
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from DB.models import create_tables

connect_info = {'drivername': 'postgresql+psycopg2',
                'username': 'postgres',
                'password': 'password',
                'host': 'localhost',
                'port': 5432,
                'database': 'vkinder'
                }


def create_db(connect):
    db = Connect(connect['username'], connect['password'], connect['database'])
    res, text = db.connect()
    if res[0]:
        res, text = db.create_db()
    print(text)
    db.close()
    return res


DSN = sqlalchemy.engine.url.URL.create(**connect_info)
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

# Session = sessionmaker(bind=engine)
# session = Session()
# session.close()
