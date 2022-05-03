from flask import request, current_app, jsonify
from flask_restful import Resource

from help_function import get_info_about_task_by_id


class Problem(Resource):
    @staticmethod
    def post(task_id):
        return get_info_about_task_by_id(task_id)
