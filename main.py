from datetime import timedelta
import os
from flask import Flask, url_for, render_template, request, redirect, make_response, current_app
from flask_jwt_simple import JWTManager
from waitress import serve
from flask_restful import reqparse, abort, Api, Resource

from calendar_data import CalendarData, WEEK_START_DAY_MONDAY
from data import db_session, is_teacher_recource
from data.users import User
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, logout_user
import smtplib

from gregorian_calendar import GregorianCalendar

my_super_app = Flask(__name__)
my_super_app.config.from_object("config")
my_super_app.config['SECRET_KEY'] = '12Wqfgr66ThSd88UI234901_qprjf'

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
def cabinet():
    calendar_id = 'calendar.json'
    GregorianCalendar.setfirstweekday(current_app.config["WEEK_STARTING_DAY"])

    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = GregorianCalendar.MONTH_NAMES[month - 1]

    if current_app.config["HIDE_PAST_TASKS"]:
        view_past_tasks = False
    else:
        view_past_tasks = request.cookies.get("ViewPastTasks", "1") == "1"

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    try:
        data = calendar_data.load_calendar(calendar_id)
    except FileNotFoundError:
        abort(404)
        print('good')

    tasks = calendar_data.tasks_from_calendar(year, month, data)
    tasks = calendar_data.add_repetitive_tasks_from_calendar(year, month, data, tasks)

    if not view_past_tasks:
        calendar_data.hide_past_tasks(year, month, tasks)

    if current_app.config["WEEK_STARTING_DAY"] == WEEK_START_DAY_MONDAY:
        weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    else:
        weekdays_headers = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    print('ok')
    return render_template(
            "calendar.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            month_name=month_name,
            current_year=current_year,
            current_month=current_month,
            current_day=current_day,
            month_days=GregorianCalendar.month_days(year, month),
            base_url=current_app.config["BASE_URL"],
            tasks=tasks,
            display_view_past_button=current_app.config["SHOW_VIEW_PAST_BUTTON"],
            weekdays_headers=weekdays_headers,
        )

@my_super_app.route('/teacher_cabinet')
@login_required
def teacher_cabinet():
    return render_template('cabinet.html', title='Личный кабинет')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    my_super_app.run(host='0.0.0.0', port=port)
