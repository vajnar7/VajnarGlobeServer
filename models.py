import os

from functools import lru_cache
from urllib.parse import quote_plus

from sqlalchemy import Boolean, create_engine, Column, Integer, String, Text, DateTime, Enum, func, LargeBinary, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.mysql import LONGBLOB
from werkzeug.security import generate_password_hash, check_password_hash
import enum

Base = declarative_base()

# Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'vajnar')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'AldebaraN7#')
DB_NAME = os.getenv('DB_NAME', 'vajnar_globe')


@lru_cache(maxsize=32)
def get_engine(host, user, password, database):
    """Return a cached SQLAlchemy engine for a given database configuration."""
    url = f'mysql+mysqlconnector://{quote_plus(user)}:{quote_plus(password)}@{host}/{database}'
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=5,
        max_overflow=10,
    )


@lru_cache(maxsize=32)
def get_session_factory(host, user, password, database):
    """Return a cached session factory using a shared engine for the database."""
    engine = get_engine(host, user, password, database)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    """Create a request-scoped database session from the shared factory."""
    return get_session_factory(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)()


class SectorEnum(enum.Enum):
    IT = 'IT'
    Kotlovnica = 'Kotlovnica'
    Elektricarji = 'Elektricarji'


class Kataster(Base):
    __tablename__ = 'kataster'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    custom = Column(Boolean, nullable=False)


class Area(Base):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    kataster_id = Column(Integer, ForeignKey('kataster.id'), nullable=False)
    kataster = relationship('Kataster', backref='areas')


user_area = Table(
    'user_area',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('area_id', ForeignKey('area.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    logged_in = Column(Boolean, nullable=False, default=False)
    areas = relationship('Area', secondary=user_area, backref='users')


class GeoPoint(Base):
    __tablename__ = 'geopoint'

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey('area.id'), nullable=False)
    latitude = Column(String(50), nullable=False)
    longitude = Column(String(50), nullable=False)
    area = relationship('Area', backref='geopoints')
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)