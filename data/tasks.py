import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import Database


# users_to_tasks = sqlalchemy.Table(
#     'users_to_tasks',
#     Database.metadata,
#     sqlalchemy.Column('users', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('users.id')),
#     sqlalchemy.Column('Tasks', sqlalchemy.Integer,
#                       sqlalchemy.ForeignKey('Tasks.id'))
# )


class SuperTasks(Database, SerializerMixin):
    __tablename__ = 'Tasks'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    type = sqlalchemy.Column(sqlalchemy.String)
    question = sqlalchemy.Column(sqlalchemy.String)
    answers = sqlalchemy.Column(sqlalchemy.String)

    lesson_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("lessons.id"))
    lesson = orm.relation('Lesson')
