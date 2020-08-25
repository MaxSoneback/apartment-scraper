
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, Float)
from scrapy.utils.project import get_project_settings

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


class Apartment(Base):
    __tablename__ = "apartment"

    id = Column('id', String(50), primary_key=True)
    type = Column('type', String(15), nullable=True)
    city = Column('city', String(30), nullable=True)
    street = Column('street', String(30), nullable=True)
    street_num = Column('street_num', String(5), nullable=True)
    district = Column('district', String(20), nullable=True)
    postal_code = Column('postal_code', Integer, nullable=True)
    latitude = Column('latitude', Float, nullable=True)
    longitude = Column('longitude', Float, nullable=True)
    rooms = Column('rooms', Integer, nullable=True)
    square_meters = Column('square_meters', Integer, nullable=True)
    floor = Column('floor', Integer, nullable=True)
    housing_society = Column('housing_society', String(40), nullable=True)
    construction_year = Column('construction_year', Integer, nullable=True)
    fee = Column('fee', Integer, nullable=True)
    price = Column('price', Integer, nullable=True)