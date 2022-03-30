import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import Database


class CalendarDB(Database, SerializerMixin):
    __tablename__ = 'calendars'

    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True,)
    calendar_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')