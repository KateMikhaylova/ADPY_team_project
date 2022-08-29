import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    last_name = sq.Column(sq.Text, nullable=False)
    first_name = sq.Column(sq.Text, nullable=False)
    patronymic = sq.Column(sq.Text, nullable=True)
    age = sq.Column(sq.Integer, nullable=True)
    id_gender = sq.Column(sq.Integer, sq.ForeignKey('gender.id'), nullable=False)
    id_city = sq.Column(sq.Integer, sq.ForeignKey('city.id'), nullable=True)
    city = relationship("City", backref='user')
    gender = relationship('Gender', backref='user')
    hobby = relationship('Hobby', backref='user')
    black_list = relationship('BlackList', backref='user')
    favorites = relationship('Favorites', backref='user')


class FoundUser(Base):
    __tablename__ = 'founduser'

    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    last_name = sq.Column(sq.Text, nullable=False)
    first_name = sq.Column(sq.Text, nullable=False)
    patronymic = sq.Column(sq.Text, nullable=True)
    age = sq.Column(sq.Integer, nullable=False)
    id_gender = sq.Column(sq.Integer, sq.ForeignKey('gender.id'), nullable=False)
    id_city = sq.Column(sq.Integer, sq.ForeignKey('city.id'), nullable=False)
    city = relationship('City', backref='founduser')
    gender = relationship('Gender', backref='founduser')
    hobby = relationship('Hobby', backref='founduser')
    black_list = relationship('BlackList', backref='founduser')
    favorites = relationship('Favorites', backref='founduser')
    photo = relationship('Photo', backref='founduser')


class City(Base):
    __tablename__ = 'city'

    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    city_name = sq.Column(sq.Text, nullable=False)

    def __str__(self):
        return f'{self.city_name}'


class Gender(Base):
    __tablename__ = 'gender'

    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    gender_name = sq.Column(sq.Text, nullable=False)


class Hobby(Base):
    __tablename__ = 'hobby'

    id = sq.Column(sq.Integer, primary_key=True, unique=True, autoincrement=True)
    hobby_name = sq.Column(sq.Text, nullable=False)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=True)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('founduser.id'), nullable=True)


class BlackList(Base):
    __tablename__ = 'blacklist'

    # id выглядит как idпользователя_idнайденнойперсоны
    id = sq.Column(sq.Text, primary_key=True, unique=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=True)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('founduser.id'), nullable=True)


class Favorites(Base):
    __tablename__ = 'favorites'

    # id выглядит как idпользователя_idнайденнойперсоны
    id = sq.Column(sq.Text, primary_key=True, unique=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=True)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('founduser.id'), nullable=True)


class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True, unique=True, autoincrement=True)
    id_photo = sq.Column(sq.Text, nullable=False)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('founduser.id'), nullable=True)


def create_tables(engine):
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        return True
    except:
        return False
