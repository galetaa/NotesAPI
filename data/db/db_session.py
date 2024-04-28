from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()

__factory = None


def global_init():
    global __factory

    if __factory:
        return

    print(f"Connecting to database")

    engine = create_engine('sqlite:///mydatabase.db')  # изменено с create_engine(URL(**DATABASE))
    __factory = sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()