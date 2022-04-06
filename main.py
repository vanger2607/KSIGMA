import os
import smtplib
from datetime import timedelta

import flask
from flask import Flask, render_template, request, redirect, make_response, current_app, jsonify, url_for
from flask_jwt_simple import JWTManager
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

from calendar_data import CalendarData, WEEK_START_DAY_MONDAY
from data import db_session, is_teacher_recource, task_resource
from data.users import User
from gregorian_calendar import GregorianCalendar
from help_function import calendar_name, students_for_teacher, get_student_id, get_info_about_task, \
    get_task_name_by_object, all_tasks, append_tasks_to_lesson

my_super_app = Flask(__name__)
my_super_app.config.from_object("config")
my_super_app.config['SECRET_KEY'] = '12Wqfgr66ThSd88UI234901_qprjf'
api = Api(my_super_app)
db_session.global_init("users.db")
login_manager = LoginManager()
login_manager.init_app(my_super_app)

my_super_app.config['JWT_SECRET_KEY'] = 'hghfehi23jksdnlqQw3244'
my_super_app.config['JWT_EXPIRES'] = timedelta(hours=45)
my_super_app.config['JWT_IDENTITY_CLAIM'] = 'user'
my_super_app.config['JWT_HEADER_NAME'] = 'authorization'
my_super_app.jwt = JWTManager(my_super_app)
api = Api(my_super_app, catch_all_404s=True)
api.add_resource(is_teacher_recource.is_TeacherResource, '/api/_is_teacher/<int:user_id>')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    grade = SelectField('Класс', choices=[5, 6, 7, 8, 9, 10, 11])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти/Зарегестрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@my_super_app.route('/')
def start():
    return render_template('index.html', title='SuperKsigma')


@my_super_app.route('/register', methods=['GET', 'POST'])
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
        try:
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.starttls()
            smtpObj.login('ax.ksigma@gmail.com', 'Alexor_2022')
            msg = 'Вы зарегистрировались в КСИГМЕ!!! С Вас теперь будут брать ежесуточно налог - 5 рублей'
            print(form.email.data)
            smtpObj.sendmail("ax.ksigma@gmail.com", form.email.data, msg.encode("utf8"))
            smtpObj.quit()
        except Exception as e:
            print(e)
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="с почтой что-то не то")
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@my_super_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            resp = make_response(redirect('/'))
            resp.set_cookie("is_teacher", str(user.is_teacher), 60 * 60 * 24 * 15)
            return resp
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@my_super_app.route('/logout')
@login_required
def logout():
    logout_user()
    res = make_response(redirect('/'))
    res.set_cookie('is_teacher', request.cookies.get('is_teacher'), max_age=0)
    return res


@my_super_app.route('/cabinet')
@login_required
def cabinet():
    return render_template('cabinet.html')


@my_super_app.route('/teacher_cabinet')
@login_required
def teacher_cabinet():
    return render_template('teacher_cabinet.html',
                           title='Личный кабинет')


@my_super_app.route('/teacher_calendar/<string:user_name>/')
@login_required
def teacher_calendar(user_name):
    calendar_title = calendar_name(get_student_id(user_name))
    students = students_for_teacher(current_user.get_id())
    current_day, current_month, current_year = GregorianCalendar.current_date()
    month_name = GregorianCalendar.MONTH_NAMES[current_month - 1]
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    try:
        data = calendar_data.load_calendar(calendar_title)
    except FileNotFoundError:
        abort(404)
    tasks = calendar_data.tasks_from_calendar(current_year, current_month, data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(current_year, current_month, data, tasks)
    weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    return render_template('calendar_teacher.html',
                           title='Личный кабинет', calendar_id=calendar_title,
                           year=current_year,
                           month=current_month,
                           month_name=month_name,
                           current_year=current_year,
                           current_month=current_month,
                           current_day=current_day,
                           month_days=GregorianCalendar.month_days(current_year, current_month),
                           base_url=current_app.config["BASE_URL"],
                           tasks=tasks,
                           display_view_past_button=current_app.config["SHOW_VIEW_PAST_BUTTON"],
                           weekdays_headers=weekdays_headers,
                           students=students,
                           username=user_name)


@my_super_app.route('/teacher/tasks', methods=['POST', 'GET'])
@login_required
def tasks():
    if request.method == 'GET':
        return render_template('teach_create_task.html', title='Создание задачи')
    elif request.method == 'POST':
        print(request.form.get('text'))
        print(request.form.get('class'))
        print(request.form.get('file'))
        return "Задача отправлена"


@my_super_app.route('/<calendar_id>/<year>/<month>/new_task', methods=['GET', 'POST'])
def new_task_action(calendar_id: str, year: int, month: int):
    if flask.request.method == 'GET':
        print('ok2')
        GregorianCalendar.setfirstweekday(current_app.config["WEEK_STARTING_DAY"])

        current_day, current_month, current_year = GregorianCalendar.current_date()
        year = max(min(int(year), current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
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
                button_default_color_value=current_app.config["BUTTON_CUSTOM_COLOR_VALUE"],
                buttons_colors=current_app.config["BUTTONS_COLORS_LIST"],
                buttons_emojis=current_app.config["BUTTONS_EMOJIS_LIST"] if emojis_enabled else tuple(),
            )


@my_super_app.route('/<calendar_id>/<year>/<month>/<day>/<task_id>/', methods=['POST', 'DELETE', 'GET'])
def delete_task(calendar_id, year, month, day, task_id):
    print('ok')
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    calendar_data.delete_task(
        calendar_id=calendar_id,
        year_str=year,
        month_str=month,
        day_str=day,
        task_id=int(task_id),
    )
    return jsonify({'success': 'OK'})
@my_super_app.route('/calendar_student')
def student_calendar():
    calendar_title = calendar_name(current_user.id)
    current_day, current_month, current_year = GregorianCalendar.current_date()
    month_name = GregorianCalendar.MONTH_NAMES[current_month - 1]
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    try:
        data = calendar_data.load_calendar(calendar_title)
    except FileNotFoundError:
        abort(404)
    tasks = calendar_data.tasks_from_calendar(current_year, current_month, data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(current_year, current_month, data, tasks)
    weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    return render_template('calendar.html',
                           title='Личный кабинет', calendar_id=calendar_title,
                           year=current_year,
                           month=current_month,
                           month_name=month_name,
                           current_year=current_year,
                           current_month=current_month,
                           current_day=current_day,
                           month_days=GregorianCalendar.month_days(current_year, current_month),
                           base_url=current_app.config["BASE_URL"],
                           tasks=tasks,
                           display_view_past_button=current_app.config["SHOW_VIEW_PAST_BUTTON"],
                           weekdays_headers=weekdays_headers)


@my_super_app.route('/create_lesson/<filter>/')
def create_lesson(filter):
    print(filter)
    if filter == 'None':
        tasks = all_tasks()
        print(tasks)
        return render_template('create_lesson.html', title='Создание уроков', tasks=tasks,
                               objects=['math', 'russia'],  base_url=current_app.config["BASE_URL"])
    else:
        tasks = get_task_name_by_object(filter)
        return render_template('create_lesson.html', title='Создание уроков', tasks=tasks,
                               objects=['math', 'russia'], base_url=current_app.config["BASE_URL"])


@my_super_app.route('/view_task/<task>/', methods=['POST', 'DELETE', 'GET'])
def view_task(task):
    task_type, questions= get_info_about_task(task)
    questions = [questions]
    print('qwe')
    print(task_type)
    return render_template('view_task.html', task_type=task_type, questions=questions)
@my_super_app.route('/lesson', methods=['POST', 'DELETE', 'GET'])
def lesson():
    lst = request.form.get('array').split(',')
    print(lst)
    append_tasks_to_lesson(lst)

    return jsonify({'succes': 'Ok'})
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    api.add_resource(task_resource.Task, '/<calendar_id>/new_task')
    my_super_app.run(host='0.0.0.0', port=port)
