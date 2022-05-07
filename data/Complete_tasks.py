import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import Database


class CompleteTasksJsons(Database, SerializerMixin):
    __tablename__ = 'complete_tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True,)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')