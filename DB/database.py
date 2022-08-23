# -*- coding: utf-8 -*-
import psycopg2
import sqlalchemy
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.orm import sessionmaker

from DB.models import create_tables

connect_info = {'drivername': 'postgresql+psycopg2',
                'username': 'postgres',
                'password': '24081986',
                'host': 'localhost',
                'port': 5432,
                'database': 'vkinder'
                }


class DB:
    '''
    Create a new :class: DB

    The standard calling form consists in sending :ref: a dictionary with data on connection to the database.
    --------------------------------------
    drivername - indicates the type of database and driver to work with.
    username - the name of the database user.
    password - the password of the administrator from the database.
    host - where the database is located. For localhost location
    port - the connection port.
    database - the name of the database.
    ---------------------------------------
    '''

    def __init__(self, **info):
        self.info = info
        dsn = sqlalchemy.engine.url.URL.create(**info)
        self.engine = sqlalchemy.create_engine(dsn)

    def newdatabase(self) -> (bool, psycopg2.Error):
        '''
        creating a new database.

        using psycopg2, a connection to the database is made
        and a new database is created using a query.
        '''
        try:
            self.connection = psycopg2.connect(user=self.info['username'],
                                               password=self.info['password'],
                                               host=self.info['host'],
                                               port=self.info['port'])

            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.__create_db()
        except (Exception, Error):
            return False, Error

    def __create_db(self):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute('create database ' + self.info['database'])
            self.__close()
        except (Exception, Error):
            return False, Error

    def __close(self):
        self.cursor.close()
        self.connection.close()
        print('Соединение закрыто')
        return True

    def preparation(self) -> sqlalchemy.engine.base.Engine:
        return self.engine

    def createtable(self, engine: sqlalchemy.engine.base.Engine) -> bool:
        '''
        From the file models.py we get a function for
        creating tables, with which we create the tables
        specified in the file in the database models.py
        :param engine:  sqlalchemy.engine.base.Engine
        :return: was it possible to create tables
        '''
        try:
            res = create_tables(engine)
            if res:
                return True
            else:
                raise
        except:
            return False

    def write(self, person: dict) -> bool:
        '''

        :param person:  dictionary with data per person
        :return: true/false was the recording successful
        '''
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.close()
        return True

    def read(self, requirement: dict) -> tuple:
        '''
        In the method, we get a dictionary with
        query parameters to search in the database.
        :param: requirement: dict
        :return: tuple
        '''
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.close()
        return ()


def main():
    work = DB(**connect_info)
    engine = work.preparation()
    test_create = work.createtable(engine)
    if not test_create:
        test_new_db = work.newdatabase()
        if test_new_db:
            work.createtable(engine)
        else:
            print(test_new_db)
            return False


if __name__ == '__main__':
    main()
