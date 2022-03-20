from flask import jsonify
from flask_restful import abort, Resource

from . import db_session
from .users import User


def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    teachers = session.query(User).get(user_id)
    if not teachers:
        abort(404, message=f"News {user_id} not found")


class is_TeacherResource(Resource):
    def get(self, user_id):
        abort_if_news_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'is_teacher': users.to_dict(
            only=('is_teacher'))})
