# -*- coding: utf-8 -*-
import psycopg2
import sqlalchemy
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.orm import sessionmaker

from DB.models import *

connect_info = {'drivername': 'postgresql+psycopg2',
                'username': 'postgres',
                'password': '24081986',
                'host': 'localhost',
                'port': 5432,
                'database': 'vkinder'
                }


class DB:
    """
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
    """

    def __init__(self, **info):
        self.info = info
        dsn = sqlalchemy.engine.url.URL.create(**info)
        self.engine = sqlalchemy.create_engine(dsn)

    def newdatabase(self) -> (bool, psycopg2.Error):
        """
        creating a new database.

        using psycopg2, a connection to the database is made
        and a new database is created using a query.
        """
        try:
            self.connection = psycopg2.connect(user=self.info['username'],
                                               password=self.info['password'],
                                               host=self.info['host'],
                                               port=self.info['port'])

            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            if self.__create_db():
                return True
        except (Exception, Error):
            return False

    def __create_db(self):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute('create database ' + self.info['database'])
            if self.__close():
                return True
        except (Exception, Error):
            return False

    def __close(self):
        self.cursor.close()
        self.connection.close()
        return True

    def preparation(self) -> sqlalchemy.engine.base.Engine:
        return self.engine

    def createtable(self, engine: sqlalchemy.engine.base.Engine) -> bool:
        """
        From the file models.py we get a function for
        creating tables, with which we create the tables
        specified in the file in the database models.py
        :param engine:  sqlalchemy.engine.base.Engine
        :return: was it possible to create tables
        """
        try:
            res = create_tables(engine)
            if res:
                return True
            else:
                raise
        except:
            return False

    def writeFoundUser(self, person: dict) -> bool:
        """
        Writing to the database of the found user
        At the beginning, we get information about the city id and gender id,
        If there are such records in the database, then we get these IDs,
        if not, then we create such data, assign the id, and then.
        Taking into account the received data, we record the user.
        :param person:  dictionary with data per person
        'firstname': person's name
        'lastname': person's surname
        'age': age of the person
        'city': person 's city
        'photos': list of id photos of a person
        'gender': gender of the person
        :return: true/false was the recording successful
        """

        q = self.__query_city(person['city'])
        if not q:
            self.__add_city(person['city'])
        id_city = self.__query_city(person['city'])
        g = self.__query_gender(person['gender'])
        if not g:
            self.__add_gender(person['gender'])
        id_gender = self.__query_gender(person['gender'])

        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = FoundUser(id=person['id_user'],
                          first_name=person['firstname'],
                          last_name=person['lastname'],
                          id_gender=id_gender,
                          id_city=id_city,
                          age=person['age'])
        session.add(query)
        session.commit()
        session.close()
        return True

    def readFoundUser(self, requirement: dict) -> tuple:
        """
        In the method, we get a dictionary with
        query parameters to search in the database.
        :param: requirement: dict
        :return: tuple
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()

        session.close()
        return ()

    def __query_gender(self, gender):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Gender).filter(Gender.gender_name == gender).all()
        session.close()
        for q in query:
            return q.id

    def __query_city(self, city):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(City).filter(City.city_name == city).all()
        session.close()
        for q in query:
            return q.id

    def __add_gender(self, gender):
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            sex = Gender(gender_name=gender)
            session.add(sex)
            session.commit()
            session.close()
            return True
        except:
            return False

    def __add_city(self, city):
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            c = City(city_name=city)
            session.add(c)
            session.commit()
            session.close()
            return True
        except:
            return False


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
            print('НИЧЕГО НЕ РАБОТАЕТ!')
            return False
    person = {'firstname': 'Лена',
              'lastname': 'Андреева',
              'id_user': '457539545',
              'age': '37',
              'city': 'Дудинка',
              'gender': 'женский',
              'photos': [('457539545_456239020', (15, 0)), ('457539545_456239024', (12, 0)),
                         ('457539545_456239045', (7, 0))]
              }
    work.writeFoundUser(person)


if __name__ == '__main__':
    main()
