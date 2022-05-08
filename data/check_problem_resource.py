from flask import request, current_app, jsonify
from flask_restful import Resource, reqparse, abort
import json
import collections
import config
from data.tasks import SuperTasks
from help_function import connect_to_db, get_object_id_by_name, get_json_name_by_user_id, get_info_about_task_by_id


def add_complete_task_to_json(us_id, dct):
    with open("data/complete_tasks_jsons/" + get_json_name_by_user_id(us_id), 'r', encoding='utf-8') as f:
        data = json.load(f)
    data.update(dct)
    print(data)
    with open("data/complete_tasks_jsons/" + get_json_name_by_user_id(us_id), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class CheckProblem(Resource):
    @staticmethod
    def post(user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('student_answers')
        parser.add_argument('task_id')
        args = parser.parse_args()
        print(args['student_answers'])
        if len(get_info_about_task_by_id(args["task_id"])) == 4:
            name, question, task_type, answers = get_info_about_task_by_id(args['task_id'])

        else:
            name, question, task_type, variations_of_answers, answers = get_info_about_task_by_id(args['task_id'])
        print(answers)
        if type(answers) == int:
            answers = str(answers)
        if ";" in answers:
            if collections.Counter(answers.split('; ')) == collections.Counter(args["student_answers"].split(';')):
                student_answers = ';'.join([i.strip() for i in args['student_answers'].split(';')])
                dct = {args["task_id"]: {"student_answers": student_answers, "correct": "correct"}}
            else:
                student_answers = ';'.join([i.strip() for i in args['student_answers'].split(';')])
                dct = {args["task_id"]: {"student_answers": student_answers.split(';'), "correct": "incorrect"}}
                add_complete_task_to_json(user_id, dct)
                return jsonify({"answers": 'incorrect'})
        else:
            if answers.strip() == args["student_answers"].strip():
                dct = {args["task_id"]: {"student_answers": args["student_answers"].split(';'), "correct": "correct"}}
                add_complete_task_to_json(user_id, dct)
                return jsonify({"answers": 'correct'})
            else:
                dct = {args["task_id"]: {"student_answers": args["student_answers"].split(';'), "correct": "incorrect"}}
                add_complete_task_to_json(user_id, dct)
                return jsonify({"answers": "incorrect"})
        add_complete_task_to_json(user_id, dct)
        return jsonify({"answers": "correct"})
