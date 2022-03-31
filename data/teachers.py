import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import Database
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import orm
class Teacher(Database, UserMixin, SerializerMixin):
    __tablename__ = 'teachers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("users.id"), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    students = sqlalchemy.Column(sqlalchemy.String, nullable=True) # id всех учеников, у которых преподает учитель.
    # Записываются через запятую пробел
    user = orm.relation('User')
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)