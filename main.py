from datetime import timedelta

from flask import Flask, url_for, render_template, request, redirect
from flask_jwt_simple import JWTManager

from data import db_session
from waitress import serve
from data.users import User
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, logout_user
import smtplib

my_super_app = Flask(__name__)
my_super_app.config['SECRET_KEY'] = '12Wqfgr66ThSd88UI234901_qprjf'

db_session.global_init("data/db/users.db")
login_manager = LoginManager()
login_manager.init_app(my_super_app)
my_super_app.config['JWT_SECRET_KEY'] = 'hghfehi23jksdnlqQw3244'
my_super_app.config['JWT_EXPIRES'] = timedelta(hours=45)
my_super_app.config['JWT_IDENTITY_CLAIM'] = 'user'
my_super_app.config['JWT_HEADER_NAME'] = 'authorization'
my_super_app.jwt = JWTManager(my_super_app)
smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.starttls()
smtpObj.login('ax.ksigma@gmail.com', 'Alexor_2022')


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
        msg = 'Вы зарегистрировались в КСИГМЕ!!! С Вас теперь будут брать ежесуточно налог - 5 рублей'
        smtpObj.sendmail("ax.ksigma@gmail.com", form.email.data, msg.encode("utf8"))
        smtpObj.quit()
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
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@my_super_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@my_super_app.route('/cabinet')
def cabinet():
    return render_template('cabinet.html', title='Личный кабинет')


if __name__ == '__main__':
    serve(my_super_app, host='0.0.0.0', port=50000)
