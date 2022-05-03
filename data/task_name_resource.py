from flask import request, current_app, jsonify
from flask_restful import Resource

from help_function import get_name_task_by_id


class NameOfTask(Resource):
    @staticmethod
    def post(task_id):
        task_name = get_name_task_by_id(task_id)
        return task_name
