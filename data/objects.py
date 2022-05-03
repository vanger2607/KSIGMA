import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from data.db_session import Database


class Objects(Database, SerializerMixin):
    __tablename__ = 'Object'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String,
                             unique=True)
