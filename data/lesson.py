import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import Database


class Lesson(Database, SerializerMixin):
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    type_object = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("Object.id"))
    object = orm.relation('Objects')

    tasks = orm.relation("SuperTasks", back_populates='lesson')

    course_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("courses.id"))
    course = orm.relation('Course')
