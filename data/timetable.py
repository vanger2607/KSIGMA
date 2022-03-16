# свое id
# id ученика к которому привязано
# id учителя, который создал расписание
# время и дата, которые назначит учитель при создании + возможность изменять
# task_id
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import Database
from sqlalchemy import orm


class Timetable(Database, SerializerMixin):
    __tablename__ = 'Timetables'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    users_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("users.id"))
    teachers_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))

    datetime = sqlalchemy.Column(sqlalchemy.DateTime)
    time = sqlalchemy.Column(sqlalchemy.Time)
    object_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("object.id"))
    object = orm.relation('Objects')
    user = orm.relation('User')
    teacher = orm.relation('Teacher')