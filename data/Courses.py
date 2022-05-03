import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import Database

courses_to_users = sqlalchemy.Table(
    'courses_to_users',
    Database.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('courses', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('courses.id'))
)


class Course(Database, SerializerMixin):
    __tablename__ = 'courses'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)

    lessons = orm.relation("Lesson", back_populates='course')

    object_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("Object.id"))
    object = orm.relation('Objects')
