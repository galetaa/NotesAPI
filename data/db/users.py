from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from data.db.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    notes = relationship('Note', backref='author', lazy=True)
