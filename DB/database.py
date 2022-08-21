# -*- coding: utf-8 -*-
import sqlalchemy

from DB.createDB import Connect
from DB.models import create_tables

'''
in connect_info we pass
drivername : database type and driver for working with it (by default postgresql+psycopg2)
username: user login in Postgresql
password: your password from Postgresql
host: where the database is located, if locally, then localhost
port: where to connect, by default 5432
database : name of the database
'''
connect_info = {'drivername': 'postgresql+psycopg2',
                'username': 'postgres',
                'password': 'password',
                'host': 'localhost',
                'port': 5432,
                'database': 'vkinder'
                }


def create_db(con: dict) -> bool:
    '''
    :param con: dictionary with database connection parameters
    :return: If the database is created returns True
    '''
    db = Connect(con['username'], con['password'], con['database'])
    res, text = db.connect()
    if res:
        res, text = db.create_db()
        db.close()
    print(text)
    return res


def preparation(info: dict) -> sqlalchemy.engine.base.Engine:
    '''
    :param info: dictionary with database connection parameters
    :return: was it possible to create tables in the database
    '''

    DSN = sqlalchemy.engine.url.URL.create(**info)
    engine = sqlalchemy.create_engine(DSN)
    return engine


def main():
    engine = preparation(connect_info)
    result = create_tables(engine)
    if result:
        print('Таблицы созданы')
    else:
        result = create_db(connect_info)
        if result:
            engine = preparation(connect_info)
            result = create_tables(engine)
            if result:
                print('Таблицы созданы')
                return True
        return False


# Session = sessionmaker(bind=engine)
# session = Session()
# session.close()

if __name__ == '__main__':
    main()
