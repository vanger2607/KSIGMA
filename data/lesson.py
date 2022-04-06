import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import Database

class Lesson(Database, SerializerMixin):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    tasks = sqlalchemy.Column(sqlalchemy.String)
