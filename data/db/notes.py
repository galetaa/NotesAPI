from sqlalchemy import Column, Integer, String, Text,ForeignKey,DateTime,func
from data.db.db_session import SqlAlchemyBase


class Note(SqlAlchemyBase):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_date = Column(DateTime, default=func.current_timestamp())
    updated_date = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
