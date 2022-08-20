import sqlalchemy
from sqlalchemy.orm import sessionmaker

from DB.models import create_tables

DSN = sqlalchemy.engine.url.URL.create(drivername='postgresql+psycopg2', username='postgres', password='postgres',
                                       host='localhost', port=5432, database='test')

engine = sqlalchemy.create_engine(DSN)

create_tables(engine)

#Session = sessionmaker(bind=engine)
#session = Session()
#session.close()
