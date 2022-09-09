# -*- coding: utf-8 -*-

import psycopg2
import sqlalchemy
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.orm import sessionmaker
from pprint import pprint

from DB.models import User, FoundUser, City, Gender, BlackList, Favorites, Photo, create_tables

connect_info = {'drivername': 'postgresql+psycopg2',
                'username': 'postgres',
                'password': 'password',
                'host': 'localhost',
                'port': 5432,
                'database': 'vkinder'
                }


# noinspection PyUnresolvedReferences
class DB:
    """
    Create a new :class: DB
    This class is an interface for working with a database.
    Creating a database, creating tables in the database,
    querying the database and creating records.
    ___________________Methods_______________________________
    new_database()
    __create_db()
    __close()
    preparation()
    create_table()
    write_user()
    write_found_user()
    __query_gender()
    __query_person()
    __query_city()
    __query_user()
    __add_gender()
    __add_city()
    query_photo()
    read_user()
    read_found_user()
    add_to_favourite()
    query_favourite()
    delete_from_favourites()
    add_to_blacklist()
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
        self.connection = None
        self.info = info
        dsn = sqlalchemy.engine.url.URL.create(**info)
        self.engine = sqlalchemy.create_engine(dsn)

    def new_database(self) -> (bool, psycopg2.Error):
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
            self.cursor.execute('create database ' + f"{self.info['database']}")
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

    @staticmethod
    def create_table(engine: sqlalchemy.engine.base.Engine) -> bool:
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

    def write_user(self, person: dict) -> bool:
        """

        :param person:
        id: str
        first_name: str
        last_name: str
        midle_name: str
        age: int
        city: int
        city_title: str
        gender: int
        gender_title: str
        :return: bool
        """
        q = self.__query_city(person['city'])
        if not q:
            self.__add_city(id=person['city'], city_title=person['city_title'])
        g = self.__query_gender(person['gender'])
        if not g:
            self.__add_gender(id=person['gender'], gender_title=person['gender_title'])
        if not self.__query_user(person):
            Session = sessionmaker(bind=self.engine)
            session = Session()
            if 'personal' in person and person['personal'] and person['personal'] is not None:
                query = User(id=person['id'],
                             first_name=person['first_name'],
                             last_name=person['last_name'],
                             middle_name=person['middle_name'],
                             id_gender=person['gender'],
                             id_city=person['city'],
                             age=person['age'],
                             activities=person['activities'],
                             books=person['books'],
                             games=person['games'],
                             interests=person['interests'],
                             movies=person['movies'],
                             music=person['music'],
                             political=person['personal'].get('political'),
                             religion_id=person['personal'].get('religion_id'),
                             life_main=person['personal'].get('life_main'),
                             people_main=person['personal'].get('people_main'),
                             smoking=person['personal'].get('smoking'),
                             alcohol=person['personal'].get('alcohol'),
                             inspired_by=person['personal'].get('inspired_by'),
                             langs=person['personal'].get('langs'),
                             relation=person['relation'],
                             tv=person['tv']
                             )
            else:
                query = User(id=person['id'],
                             first_name=person['first_name'],
                             last_name=person['last_name'],
                             middle_name=person['middle_name'],
                             id_gender=person['gender'],
                             id_city=person['city'],
                             age=person['age'],
                             activities=person['activities'],
                             books=person['books'],
                             games=person['games'],
                             interests=person['interests'],
                             movies=person['movies'],
                             music=person['music'],
                             relation=person['relation'],
                             tv=person['tv']
                             )
            session.add(query)
            session.commit()
            session.close()
        return True

    def write_found_user(self, person: dict) -> bool:
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
            if 'personal' in person and person['personal'] and person['personal'] is not None:
                query = FoundUser(id=person['id_user'],
                                  first_name=person['first_name'],
                                  last_name=person['last_name'],
                                  middle_name=person['middle_name'],
                                  id_gender=person['gender'],
                                  id_city=person['city'],
                                  age=person['age'],
                                  activities=person['activities'],
                                  books=person['books'],
                                  games=person['games'],
                                  interests=person['interests'],
                                  movies=person['movies'],
                                  music=person['music'],
                                  political=person['personal'].get('political'),
                                  religion_id=person['personal'].get('religion_id'),
                                  life_main=person['personal'].get('life_main'),
                                  people_main=person['personal'].get('people_main'),
                                  smoking=person['personal'].get('smoking'),
                                  alcohol=person['personal'].get('alcohol'),
                                  inspired_by=person['personal'].get('inspired_by'),
                                  langs=person['personal'].get('langs'),
                                  relation=person['relation'],
                                  tv=person['tv'])
            else:
                query = FoundUser(id=person['id_user'],
                                  first_name=person['first_name'],
                                  last_name=person['last_name'],
                                  middle_name=person['middle_name'],
                                  id_gender=person['gender'],
                                  id_city=person['city'],
                                  age=person['age'],
                                  activities=person['activities'],
                                  books=person['books'],
                                  games=person['games'],
                                  interests=person['interests'],
                                  movies=person['movies'],
                                  music=person['music'],
                                  relation=person['relation'],
                                  tv=person['tv'])
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

    def __query_user(self, person):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(User).filter(User.id == person['id']).all()
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

    def query_photo(self, id_found_user: int) -> list:
        """
        Getting a list of user's photos by id
        :param id_found_user:
        :return:
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(Photo.id_photo).filter(Photo.id_found_user == id_found_user).all()
        session.close()
        photos = []
        for q in query:
            photos.append(q[0])
        return photos

    def read_user(self, id_user: int):
        """
        Getting user data first name, last name, id
        :param id_user:
        :return:
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        query = session.query(User).filter(User.id == id_user).all()
        result = []
        if query:
            for q in query:
                result.append({'first_name': q.first_name,
                               'last_name': q.last_name,
                               'id_user': q.id,
                               'city': q.id_city,
                               'age': q.age,
                               'activities': q.activities,
                               'books': q.books,
                               'games': q.games,
                               'interests': q.interests,
                               'movies': q.movies,
                               'music': q.music,
                               'political': q.political,
                               'religion_id': q.religion_id,
                               'life_main': q.life_main,
                               'people_main': q.people_main,
                               'smoking': q.smoking,
                               'alcohol': q.alcohol,
                               'inspired_by': q.inspired_by,
                               'langs': q.langs,
                               'relation': q.relation,
                               'tv': q.tv
                               })
        return result

    def read_found_user(self, bot_user_id: int, requirement: dict) -> list:
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
        subquery_list = []
        for result in subquery:
            subquery_list.append(result[0])

        query = session.query(FoundUser).filter(FoundUser.id_gender == requirement['gender'],
                                                FoundUser.id_city == requirement['city'],
                                                FoundUser.age == requirement['age'],
                                                FoundUser.id.not_in(subquery_list)).all()

        session.close()
        result = []
        for q in query:
            result.append({'first_name': q.first_name,
                           'last_name': q.last_name,
                           'id_user': q.id,
                           'city': q.id_city,
                           'age': q.age,
                           'activities': q.activities,
                           'books': q.books,
                           'games': q.games,
                           'interests': q.interests,
                           'movies': q.movies,
                           'music': q.music,
                           'political': q.political,
                           'religion_id': q.religion_id,
                           'life_main': q.life_main,
                           'people_main': q.people_main,
                           'smoking': q.smoking,
                           'alcohol': q.alcohol,
                           'inspired_by': q.inspired_by,
                           'langs': q.langs,
                           'relation': q.relation,
                           'tv': q.tv
                           })
        return result

    def add_to_favourite(self, id_user: int, id_found_user: int) -> bool:
        """
        add the found user to the favorites list
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

    def query_favourite(self, user_id: int) -> list:
        """
        Getting a list of favorites by user id
        :param user_id: int
        :return: list
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        subquery = session.query(Favorites.id_found_user).filter(Favorites.id_user == user_id).all()
        subquery_list = [i[0] for i in subquery]
        query = session.query(FoundUser).filter(FoundUser.id.in_(subquery_list)).all()
        session.close()
        return query

    def delete_from_favourites(self, id_user, id_found_user):
        """
        remove from Favorites list
        id_record - in the form of: 'id_user'_'id_found_user'
        for example 44556677_1234567
        :param id_user: int
        :param id_found_user: int
        :return: bool
        """
        Session = sessionmaker(bind=self.engine)
        session = Session()
        favourite = session.query(Favorites).filter(Favorites.id_user == id_user,
                                                    Favorites.id_found_user == id_found_user).all()
        if favourite:
            session.delete(favourite[0])
            session.commit()
            session.close()

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
    test_create = work.create_table(engine)
    if not test_create:
        test_new_db = work.new_database()
        if test_new_db:
            work.create_table(engine)
        else:
            print(test_new_db)
            print('НИЧЕГО НЕ РАБОТАЕТ!')
            return False


if __name__ == '__main__':
    main()
