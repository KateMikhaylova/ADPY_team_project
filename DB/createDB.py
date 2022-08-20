import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Connect:
    '''
    '''

    def __init__(self, user: str, password: str, db_name: str, host='localhost', port='5432'):
        '''

        :param user:
        :param password:
        :param db_name:
        :param host:
        :param port:
        '''
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name

    def connect(self):
        '''

        :return:
        '''
        try:
            self.connection = psycopg2.connect(user=self.user,
                                               password=self.password,
                                               host=self.host,
                                               port=self.port)

            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return True, 'Успешное соединение'
        except (Exception, Error):
            return False, Error

    def create_db(self):
        '''

        :return:
        '''
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute('create database ' + self.db_name)
            return True, 'База данных создана'
        except (Exception, Error):
            return False, Error

    def close(self):
        self.cursor.close()
        self.connection.close()
        print('Соединение закрыто')
