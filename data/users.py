import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

from data.db_session import Database


class User(Database, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True,
                                        unique=True)

    courses = orm.relation("Course",
                           secondary="courses_to_users",
                           backref="courses")

    # служебныве поля чтобы собрать учеников и учителей в 1й форме авторизации
    is_teacher = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    # Служебные поля учеников
    grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    # Служебные поля учителей
    student_ids = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
