import psycopg2
import sqlalchemy
from sqlalchemy.orm import sessionmaker

connect_to_db_info = {
    'login': 'postgres',
    'password': 'postgres',
    'database_name': 'vkinder'
}


def create_dsn(login, password, database_name):
    return 'postgresql://' + login + ':' + password + '@localhost:5432' + '/' + database_name


DSN = create_dsn(**connect_to_db_info)
engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()
session.close()
