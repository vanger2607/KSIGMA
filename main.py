import json
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from datetime import timedelta
from urllib.parse import unquote

import flask
import werkzeug
from flask import current_app, Flask, jsonify, make_response, redirect, \
    render_template, request
from flask_jwt_simple import JWTManager
from flask_login import current_user, login_required, login_user, LoginManager, \
    logout_user
from flask_restful import abort, Api, reqparse
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, \
    SubmitField, TextAreaField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

import config
from Errors import Badlesson, BadCourse
from calendar_data import CalendarData
from data import db_session, task_resource, is_teacher_recource, problem_resource, save_problem_resource, \
    task_name_resource
from data.calendar import CalendarDB
from data.users import User
from gregorian_calendar import GregorianCalendar
from help_function import all_tasks, creation_lesson, calendar_name, \
    get_info_about_task, get_student_id, students_for_teacher, is_teacher, get_task_names_by_object, all_lessons, \
    get_lesson_names_by_object, creation_course, all_courses, get_lessons_by_course, get_lesson_name_by_id, \
    chang_course, get_course_by_subject, get_all_task_from_lesson

application = Flask(__name__)
application.config.from_object("config")
application.config['SECRET_KEY'] = '12Wqfgr66ThSd88UI234901_qprjf'
api = Api(application)
db_session.global_init("Site.db")
login_manager = LoginManager()
login_manager.init_app(application)

application.config['JWT_SECRET_KEY'] = 'hghfehi23jksdnlqQw3244'
application.config['JWT_EXPIRES'] = timedelta(hours=45)
application.config['JWT_IDENTITY_CLAIM'] = 'user'
application.config['JWT_HEADER_NAME'] = 'authorization'
application.jwt = JWTManager(application)
api = Api(application, catch_all_404s=True)
api.add_resource(is_teacher_recource.is_TeacherResource,
                 '/api/_is_teacher/<int:user_id>')



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    grade = SelectField('Класс', choices=[5, 6, 7, 8, 9, 10, 11])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти/Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class LessonForm(FlaskForm):
    text_name = StringField('название урока', validators=[DataRequired()])


@application.errorhandler(werkzeug.exceptions.Forbidden)
def handle_bad_request(e):
    return 'This page is only for teachers, ha-ha-ha loser!', 400




@application.route('/')
def start():
    return render_template('index.html', title='SuperKsigma')


@application.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            grade=form.grade.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        with open(form.name.data + '.json', 'w') as f:
            data = {'tasks': {'normal': {}, "repetition": [], "hidden_repetition": {}}}
            new_json = json.dump(data, f, indent=4, ensure_ascii=False)
        db_sess.commit()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        student_id = user.id
        calendar = CalendarDB(student_id=student_id, calendar_name=form.name.data + '.json')
        db_sess = db_session.create_session()
        db_sess.add(calendar)
        db_sess.commit()
        try:
            my_html = f"""
             <html>
               <body>
                 <p>Уважаемый {form.email.data}! Вы зарегистрировались в KSIGMA!  <i>немного о нас: наш сайт создан для помощи в обучении <i>
                 он предназначен для репетиторов и их учеников, таких как {form.name.data}.
                 Мы очень рады, что сам {form.name.data} зашел на наш сайт и надеемся, что он Вам понравится.<br>
                 Мы заметили,  Вы учитесь в {form.grade.data} классе. Так что, возможно {form.name.data}у/е
                  будет интересна эта <strong> информация </strong>:
                    <a href="https://clck.ru/ghaFp"> репетитор по математике для подготовки к  огэ </a>
                    Хорошего дня {form.email.data}
                 </p>
               </body>
             </html>
             """
            subject = 'регистрация в ксигме'
            msg = MIMEMultipart("alternative")
            msg['From'] = 'superksigma@yandex.ru'
            msg['Subject'] = Header(subject, 'utf-8')
            msg['To'] = Header(form.email.data, 'utf-8')
            part2 = MIMEText(my_html, "html")
            msg.attach(part2)
            print(form.email.data)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.yandex.ru", 465, context=context) as server:
                server.login(config.SENDER_EMAIL, config.PASSWORD_EMAIL)
                server.sendmail(
                    config.SENDER_EMAIL, form.email.data, msg.as_string()
                )
        except Exception as e:
            print(e)
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="с почтой что-то не то")
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            resp = make_response(redirect('/'))
            resp.set_cookie("is_teacher", str(user.is_teacher),
                            60 * 60 * 24 * 15)
            return resp
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    res = make_response(redirect('/'))
    is_teacher_cookies = request.cookies.get('is_teacher'),
    print(is_teacher_cookies)
    if not (is_teacher_cookies[0] is None):
        res.set_cookie('is_teacher', request.cookies.get('is_teacher'), max_age=0)
    return res


@application.route('/cabinet')
@login_required
def cabinet():
    return render_template('cabinet.html')


@application.route('/teacher_cabinet')
@login_required
def teacher_cabinet():
    return render_template('teacher_cabinet.html',
                           title='Личный кабинет')


@application.route('/teacher_calendar/<string:user_name>/')
@login_required
def teacher_calendar(user_name):
    if is_teacher(current_user.get_id()):
        calendar_title = calendar_name(get_student_id(user_name))
        students = students_for_teacher(current_user.get_id())
        current_day, current_month, current_year = GregorianCalendar.current_date()
        month_name = GregorianCalendar.MONTH_NAMES[current_month - 1]
        calendar_data = CalendarData(current_app.config["DATA_FOLDER"],
                                     current_app.config["WEEK_STARTING_DAY"])
        try:
            data = calendar_data.load_calendar(calendar_title)
        except FileNotFoundError:
            abort(404)
        tasks = calendar_data.tasks_from_calendar(current_year, current_month,
                                                  data)
        tasks = calendar_data.add_repetitive_tasks_from_calendar(current_year,
                                                                 current_month,
                                                                 data, tasks)
        weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        return render_template('calendar_teacher.html',
                               title='Личный кабинет', calendar_id=calendar_title,
                               year=current_year,
                               month=current_month,
                               month_name=month_name,
                               current_year=current_year,
                               current_month=current_month,
                               current_day=current_day,
                               month_days=GregorianCalendar.month_days(
                                   current_year, current_month),
                               base_url=current_app.config["BASE_URL"],
                               tasks=tasks,
                               display_view_past_button=current_app.config[
                                   "SHOW_VIEW_PAST_BUTTON"],
                               weekdays_headers=weekdays_headers,
                               students=students,
                               username=user_name)
    else:
        abort(403)


@application.route('/teacher/tasks', methods=['POST', 'GET'])
@login_required
def tasks():
    if is_teacher(current_user.get_id()):
        if request.method == 'GET':
            return render_template('teach_create_task.html',
                                   title='Создание задачи', subjects=config.SUBJECTS)
    else:
        abort(403)


@application.route('/teacher/check_tasks', methods=['POST'])
@login_required
def check_tasks():
    try:
        parser = reqparse.RequestParser()
        parser.add_argument('file')
        parser.add_argument('task_name')
        parser.add_argument('lesson_name')
        args = parser.parse_args()
        files_s = args["file"]
        task_name = args['task_name']
        lesson_name = args['lesson_name']
        print(files_s)
        files_s = files_s.split('/')
        file = {}
        for i in files_s:
            file[i.split(':')[0].strip().lower()] = i.split(':')[1].strip()
        print(file)
        if 'variations_of_answers' in file and len(file['answers']) > 1:
            task_type = 'check-boxes'
            if ';' not in file['questions']:
                questions = [file['questions']]
            else:
                questions = file['questions'].split('; ')
            variations_of_answers = file['variations_of_answers'].split(';')
            answers = file['answers'].split('; ')
            return render_template('teach_check.html', task_type=task_type, questions=questions,
                                   variations_of_answers=variations_of_answers, task_name=task_name,
                                   lesson_name=lesson_name, answers=answers)
        elif 'variations_of_answers' in file and len(file['answers']) == 1:
            task_type = 'radio-buttons'
            if ';' not in file['questions']:
                questions = [file['questions']]
            else:
                questions = file['questions'].split('; ')
            answers = file['answers']
            answers = answers.split('; ')
            variations_of_answers = file['variations_of_answers'].split('; ')
            print(variations_of_answers)
            return render_template('teach_check.html', task_type=task_type, questions=questions,
                                   variations_of_answers=variations_of_answers, task_name=task_name,
                                   lesson_name=lesson_name, answers=answers)
        else:
            task_type = 'open'
            if ';' not in file['questions']:
                questions = [file['questions']]
            else:
                questions = file['questions'].split('; ')
            print(questions)
            answers = file['answers']
            if len(answers) >= 4:
                answers = answers.split('; ')
            return render_template('teach_check.html', task_type=task_type, questions=questions, task_name=task_name,
                                   lesson_name=lesson_name, answers=answers, variations_of_answers='0')

    except KeyError:
        print('ok')
        return render_template('teach_create_task.html',
                               title='Создание задачи', subjects=config.SUBJECTS, messages='Неверные данные в файле')
    except IndexError:
        print('ok1')
        return render_template('teach_create_task.html',
                               title='Создание задачи', subjects=config.SUBJECTS, messages='Неверные данные в файле')
@application.route('/<calendar_id>/<year>/<month>/new_task',
                   methods=['GET', 'POST'])
def new_task_action(calendar_id: str, year: int, month: int):
    if flask.request.method == 'GET':
        GregorianCalendar.setfirstweekday(
            current_app.config["WEEK_STARTING_DAY"])

        current_day, current_month, current_year = GregorianCalendar.current_date()
        year = max(min(int(year), current_app.config["MAX_YEAR"]),
                   current_app.config["MIN_YEAR"])
        month = max(min(int(month), 12), 1)
        month_names = GregorianCalendar.MONTH_NAMES

        if current_month == month and current_year == year:
            day = current_day
        else:
            day = 1
        day = int(request.args.get("day", day))

        task = {
            "date": CalendarData.date_for_frontend(year, month, day),
            "is_all_day": True,
            "repeats": False,
            "details": "",
        }

        emojis_enabled = current_app.config.get("EMOJIS_ENABLED", False)

        return render_template(
            "task.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            min_year=current_app.config["MIN_YEAR"],
            max_year=current_app.config["MAX_YEAR"],
            month_names=month_names,
            task=task,
            base_url=current_app.config["BASE_URL"],
            editing=False,
            emojis_enabled=emojis_enabled,
            button_default_color_value=current_app.config[
                "BUTTON_CUSTOM_COLOR_VALUE"],
            buttons_colors=current_app.config["BUTTONS_COLORS_LIST"],
            buttons_emojis=current_app.config[
                "BUTTONS_EMOJIS_LIST"] if emojis_enabled else tuple(),
        )


@application.route('/<calendar_id>/<year>/<month>/<day>/<task_id>/',
                   methods=['POST', 'DELETE', 'GET'])
def delete_task(calendar_id, year, month, day, task_id):
    print('ok')
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"],
                                 current_app.config["WEEK_STARTING_DAY"])
    calendar_data.delete_task(
        calendar_id=calendar_id,
        year_str=year,
        month_str=month,
        day_str=day,
        task_id=int(task_id),
    )
    return jsonify({'success': 'OK'})


@application.route('/calendar_student')
def student_calendar():
    calendar_title = calendar_name(current_user.id)
    current_day, current_month, current_year = GregorianCalendar.current_date()
    month_name = GregorianCalendar.MONTH_NAMES[current_month - 1]
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"],
                                 current_app.config["WEEK_STARTING_DAY"])
    try:
        data = calendar_data.load_calendar(calendar_title)
    except FileNotFoundError:
        abort(404)
    tasks = calendar_data.tasks_from_calendar(current_year, current_month,
                                              data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(current_year,
                                                             current_month,
                                                             data, tasks)
    weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    return render_template('calendar.html',
                           title='Личный кабинет', calendar_id=calendar_title,
                           year=current_year,
                           month=current_month,
                           month_name=month_name,
                           current_year=current_year,
                           current_month=current_month,
                           current_day=current_day,
                           month_days=GregorianCalendar.month_days(
                               current_year, current_month),
                           base_url=current_app.config["BASE_URL"],
                           tasks=tasks,
                           display_view_past_button=current_app.config[
                               "SHOW_VIEW_PAST_BUTTON"],
                           weekdays_headers=weekdays_headers)


@application.route('/create_lesson/<filter_name>/', methods=["GET", "POST"])
def create_lesson(filter_name):
    form = LessonForm()
    if filter_name == 'None':
        tasks_ = all_tasks()
        return (render_template('create_lesson.html', title='Создание уроков',
                                tasks=tasks_,
                                objects=['math', 'russia'],
                                base_url=current_app.config["BASE_URL"],
                                object_now=filter_name, form=form))
    else:
        tasks_ = get_task_names_by_object(filter_name)
        return render_template('create_lesson.html', title='Создание уроков',
                               tasks=tasks_,
                               objects=['math', 'russia'],
                               base_url=current_app.config["BASE_URL"],
                               object_now=filter_name, form=form)


@application.route('/view_task/<task>/', methods=['POST', 'DELETE', 'GET'])
def view_task(task):
    task_type, questions = get_info_about_task(task)
    questions = [questions]
    return render_template('view_task.html', task_type=task_type,
                           questions=questions)


@application.route('/lesson', methods=['POST'])
def lesson():
    lst = request.form.get('array').split(',')
    name = request.form.get('name')
    try:
        creation_lesson(lst, name)
    except Badlesson:
        return jsonify({'sucess': 'bad'})
    return jsonify({'succes': 'Ok'})


@application.route('/create_courses/<filter_name>/', methods=["GET", "POST"])
def create_cour(filter_name):
    form = LessonForm()
    if filter_name == 'None':
        lessons = all_lessons()

        return (render_template('courses.html', title='Создание курсов',
                                lessons=lessons,
                                objects=['math', 'russia'],
                                base_url=current_app.config["BASE_URL"],
                                object_now=filter_name, form=form))
    else:
        lessons = get_lesson_names_by_object(filter_name)
        print(lessons)
        return render_template('courses.html', title='Создание курсов',
                               lessons=lessons,
                               objects=['math', 'russia'],
                               base_url=current_app.config["BASE_URL"],
                               object_now=filter_name, form=form, )


@application.route('/course', methods=['POST'])
def course():
    lst = request.form.get('array').split(',')
    name = request.form.get('name')
    try:
        creation_course(lst, name)
    except BadCourse:
        return jsonify({'sucess': 'bad'})
    return jsonify({'succes': 'Ok'})


@application.route('/change_course/<filter_name>/')
def change_course(filter_name):
    form = LessonForm()
    courses = all_courses()
    print(courses)
    lessons = all_lessons()
    if filter_name == 'None':

        return (render_template('change_courses.html', title='Создание курсов',
                                lessons=lessons,
                                objects=['math', 'russia'],
                                base_url=current_app.config["BASE_URL"],
                                course_now=filter_name, form=form, courses=courses))
    else:
        lessons_cr = get_lessons_by_course(filter_name)
        lessons_cr = [get_lesson_name_by_id(i) for i in lessons_cr]
        print(lessons_cr)
        return render_template('change_courses.html', title='Создание курсов',
                               lessons=lessons,
                               objects=['math', 'russia'],
                               base_url=current_app.config["BASE_URL"],
                               course_now=filter_name, form=form, courses=courses, lessons_cr=lessons_cr)


@application.route('/help_filter/<filter_name>/', methods=['POST', 'GET'])
def help_lesson(filter_name):
    lst = get_lesson_names_by_object(filter_name)
    return jsonify({'lst': lst})


@application.route('/changing_course', methods=['POST'])
def changing_course():
    lst = request.form.get('array').split(',')
    name = request.form.get('name')
    try:
        chang_course(lst, name)
    except BadCourse:
        return jsonify({'sucess': 'bad'})
    return jsonify({'succes': 'Ok'})


@application.route('/course_student')
def course_from_student():
    return render_template('courses_student.html', title='курсы КСИГМЫ', subjects=config.SUBJECTS)


@application.route('/course_student/<subject>/')
def course_in(subject):
    courses = get_course_by_subject(subject)
    return render_template('courses_in.html', title='курсы КСИГМЫ', courses=courses)


@application.route('/course_student_lessons/<course>/')
def course_lessons_student(course):
    try:
        lessons = get_lessons_by_course(course)
        lessons = [get_lesson_name_by_id(i) for i in lessons]
    except TypeError:
        course = unquote(course)
        lessons = get_lessons_by_course(course)
        lessons = [get_lesson_name_by_id(i) for i in lessons]
    return render_template('lessons_in_courses_student.html', title='ДОМАШКА', lessons=lessons)


@application.route('/tasks_in/<lesson>/view')
def view_tasks(lesson):
    tasks = get_all_task_from_lesson(lesson)
    return render_template('tasks_in_lessons.html', title='ЗАДАЧИ', lesson=lesson,
                           tasks=tasks, base_url=current_app.config["BASE_URL"])


if __name__ == '__main__':
    api.add_resource(task_resource.Task, '/<calendar_id>/new_task')
    api.add_resource(problem_resource.Problem, '/info_task/<task_id>/')
    api.add_resource(save_problem_resource.SaveProblem,
                     '/save_problem/<task_type>/')
    api.add_resource(task_name_resource.NameOfTask,
                     '/task_name/<task_id>/')
    application.run(host='0.0.0.0')
