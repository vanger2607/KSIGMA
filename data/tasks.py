import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import Database
from sqlalchemy import orm

class SuperTasks(Database, SerializerMixin):
    __tablename__ = 'Tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    type_object = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("Object.id"))
    type = sqlalchemy.Column(sqlalchemy.String)
    question = sqlalchemy.Column(sqlalchemy.String)
    variations_of_answers =sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answers = sqlalchemy.Column(sqlalchemy.String)
    object = orm.relation('Objects')