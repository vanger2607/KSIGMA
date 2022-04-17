import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import Database


class Course(Database, SerializerMixin):
    __tablename__ = 'courses'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    lessons = sqlalchemy.Column(sqlalchemy.String)
    object = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("Object.id"))
    objects = orm.relation('Objects')