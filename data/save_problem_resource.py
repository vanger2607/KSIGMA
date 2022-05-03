from flask import request, current_app, jsonify
from flask_restful import Resource, reqparse, abort

import config
from data.tasks import SuperTasks
from help_function import connect_to_db, get_object_id_by_name


class SaveProblem(Resource):
    @staticmethod
    def post(task_type):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('subject')
            parser.add_argument('task_name')
            parser.add_argument('variations_of_answers')
            parser.add_argument('questions')
            parser.add_argument('answers')
            args = parser.parse_args()
            questions = args['questions']
            print(questions, '1')
            if type(questions) == list:
                questions = [i.replace('&39', '') for i in questions]
                questions = ''.join(questions)
            print(questions)
            answers = args['answers']
            if type(answers) == list:
                answers = [i.replace('&39', '') for i in answers]
                answers = ', '.join(answers)
            variations_of_answers = args['variations_of_answers']
            if type(variations_of_answers) == list:
                variations_of_answers = [i.replace('&39', '') for i in variations_of_answers]
                ''.join(variations_of_answers)
            if task_type == 'open':
                db_sess = connect_to_db(config.DB_NAME)
                task = SuperTasks(name=args['task_name'],
                                  type_object=get_object_id_by_name(args['subject']),
                                  question=questions,
                                  type=task_type,
                                  answers=answers)
                db_sess.add(task)
                db_sess.commit()
            elif task_type == 'radio-buttons' or task_type == 'check-boxes':
                db_sess = connect_to_db(config.DB_NAME)
                task = SuperTasks(name=args['task_name'],
                                  type_object=get_object_id_by_name(args['subject']),
                                  question=questions,
                                  type=task_type,
                                  answers=answers,
                                  variations_of_answers= variations_of_answers)
                db_sess.add(task)
                db_sess.commit()
            else:
                abort(500)
            return jsonify({'success': 'OK'})
        except Exception as e:
            abort(500)
