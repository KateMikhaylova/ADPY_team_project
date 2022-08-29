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

    """

    def __init__(self, **info: dict):
        """
            The standard calling form consists in sending :ref: a dictionary with data on connection to the database.
            :param info: dict
            --------------------------------------
            drivername - indicates the type of database and driver to work with.
            username - the name of the database user.
            password - the password of the administrator from the database.
            host - where the database is located. For localhost location
            port - the connection port.
            database - the name of the database.
            ---------------------------------------
        """
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
        'id_user': person id in VK
        'first_name': person's name
        'last_name': person's surname
        'age': age of the person
        'city': person 's id_city
        'city_title: user city title
        'photos': list of id photos of a person
        'gender': id_gender of the person
        'gender_title': user_gender_title
        :return: true/false was the recording successful
        """

        q = self.__query_city(person['city'])
        if not q:
            self.__add_city(id=person['city'], city_title=person['city_title'])
        g = self.__query_gender(person['gender'])
        if not g:
            self.__add_gender(id=person['gender'], gender_title=person['gender_title'])
        if not self.__query_person(person):
            Session = sessionmaker(bind=self.engine)
            session = Session()
            query = FoundUser(id=person['id_user'],
                              first_name=person['first_name'],
                              last_name=person['last_name'],
                              id_gender=person['gender'],
                              id_city=person['city'],
                              age=person['age'])
            session.add(query)
            record_photo = []
            for photo in person['photos']:
                record_photo.append(Photo(id_photo=photo, id_found_user=person['id_user']))
            session.add_all(record_photo)
            session.commit()
            session.close()
        return True

    def __query_gender(self, gender: int) -> int:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Gender).filter(Gender.id == gender).all()
        session.close()
        for q in query:
            return q.id

    def __query_city(self, city: id) -> int:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(City).filter(City.id == city).all()
        session.close()
        for q in query:
            return q.id

    def __query_person(self, person: dict) -> bool:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(FoundUser).filter(FoundUser.id == person['id_user']).all()
        session.close()
        if query:
            return True
        else:
            return False

    def __add_gender(self, **gender_info) -> bool:
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            sex = Gender(**gender_info)
            session.add(sex)
            session.commit()
            session.close()
            return True
        except:
            return False

    def __add_city(self, **city_info) -> bool:
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            c = City(**city_info)
            session.add(c)
            session.commit()
            session.close()
            return True
        except:
            return False

    # получение фото
    def query_photo(self, id_found_user: int) -> list:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Photo.id_photo).filter(Photo.id_found_user == id_found_user).all()
        session.close()
        photos = []
        for q in query:
            photos.append(q[0])
        return photos

    def readFoundUser(self, bot_user_id: int, requirement: dict) -> tuple:
        """
        Search for a user in the database
        :param bot_user_id: int - id of the user who is looking for a mate
        :param requirement: dict
        'gender':int - id gender
        'city':int - id city
        'age':int - person age
        :return:
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        subquery = session.query(BlackList.id_found_user).filter(BlackList.id_user == bot_user_id).all()
        query = session.query(FoundUser).filter(FoundUser.id_gender == requirement['gender'],
                                                FoundUser.id_city == requirement['city'],
                                                FoundUser.age == requirement['age'], FoundUser.id.not_in(subquery))
        # ~FoundUser.id.in_(subquery)) второй вариант, если первый не сработает
        session.close()
        result = []
        for q in query:
            result.append({'first_name': q.first_name,
                           'last_name': q.last_name,
                           'id_user': q.id})
        return result

    # Запись в избранное
    def add_to_favourite(self, id_user: int, id_found_user: int) -> bool:
        """
        id_record - в виде iduser_idfounduser
        for example 44556677_1234567
        :param id_user: int
        :param id_found_user: int
        :return: bool
        """
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            id_record = f'{id_user}_{id_found_user}'
            fav = Favorites(id=id_record, id_user=id_user, id_found_user=id_found_user)
            session.add(fav)
            session.commit()
            session.close()
            return True
        except:
            return False

    def add_to_blacklist(self, id_user, id_found_user) -> bool:
        """
        add a person to the blacklist
        id_record - in the form of: 'id_user'_'id_found_user'
        for example 44556677_1234567
        :param id_user: int
        :param id_found_user: int
        :return: bool
        """
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            id_record = f'{id_user}_{id_found_user}'
            bl = BlackList(id=id_record, id_user=id_user, id_found_user=id_found_user)
            session.add(bl)
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

    person = {'first_name': 'Лена',
              'last_name': 'Андреева',
              'midle_name': None,
              'id_user': 457539545,
              'age': 37,
              'city': 312,
              'city_title': 'Дудинка',
              'gender': 1,
              'gender_title': 'женский',
              'photos': ['457539545_456239020', '457539545_456239024',
                         '457539545_456239045']
              }
    person2 = {'first_name': 'Светлана',
               'last_name': 'Иванова',
               'id_user': 123456789,
               'age': 37,
               'city_title': 'Дудинка',
               'city': 312,
               'gender': 1,
               'gender_title': 'женский',
               'midle_name': None,
               'photos': ['123456789_456239020', '123456789_456239024',
                          '123456789_456239045']
               }
    person3 = {'first_name': 'Айгуль',
               'last_name': 'Магомедова',
               'id_user': 90000232,
               'midle_name': 'Рашид-кызы',
               'age': 37,
               'city': 200,
               'city_title': 'Якутск',
               'gender_title': 'женский',
               'gender': 1,
               'photos': ['457232539545_456239020', '457539322545_456239024',
                          '457539532245_456239045']
               }
    test = {
        'gender': 1,
        'city': 312,
        'age': 37
    }
    work.writeFoundUser(person)
    work.writeFoundUser(person2)
    work.writeFoundUser(person3)
    res = work.readFoundUser(bot_user_id=123412, requirement=test)
    if res:
        for person in res:
            photo = work.query_photo(person['id_user'])
            print(person['id_user'], person['first_name'], person['last_name'], photo)
    else:
        print('Пусто мана')


if __name__ == '__main__':
    main()
