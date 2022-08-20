import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    surname = sq.Column(sq.Text, nullable=False)
    name = sq.Column(sq.Text, nullable=False)
    patronymic = sq.Column(sq.Text, nullable=True)
    age = sq.Column(sq.Integer, nullable=False)
    id_gender = sq.Column(sq.Integer, sq.ForeignKey('gender.id'), nullable=False)
    id_city = sq.Column(sq.Integer, sq.ForeignKey('city.id'), nullable=False)


class FoundUser(Base):
    __tablename__ = 'found_user'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    surname = sq.Column(sq.Text, nullable=False)
    name = sq.Column(sq.Text, nullable=False)
    patronymic = sq.Column(sq.Text, nullable=True)
    age = sq.Column(sq.Integer, nullable=False)
    id_gender = sq.Column(sq.Integer, sq.ForeignKey('gender.id'), nullable=False)
    id_city = sq.Column(sq.Integer, sq.ForeignKey('city.id'), nullable=False)


class City(Base):
    __tablename__ = 'city'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    city_name = sq.Column(sq.Text, nullable=False)


class Gender(Base):
    __tablename__ = 'gender'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    gender_name = sq.Column(sq.Text, nullable=False)


class Hobby(Base):
    __tablename__ = 'hobby'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    hobby_name = sq.Column(sq.Text, nullable=False)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=True)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('found_user.id'), nullable=True)


class Black_list(Base):
    __tablename__ = 'black_list'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=True)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('found_user.id'), nullable=True)


class Favorites(Base):
    __tablename__ = 'favorites'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=True)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('found_user.id'), nullable=True)


class Photo(Base):
    __tablename__ = 'photo'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    link = sq.Column(sq.Text, nullable=False)
    amount = sq.Column(sq.Integer, nullable=True)
    id_found_user = sq.Column(sq.Integer, sq.ForeignKey('found_user.id'), nullable=True)
