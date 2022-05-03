import os

import flask
from flask import current_app, Flask, jsonify, redirect, \
    render_template, request
from flask_login import current_user, login_required, login_user, LoginManager, \
    logout_user
from flask_restful import abort, Api
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, \
    SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

from calendar_data import CalendarData
from data import db_session, task_resource
from data.lesson import Lesson
from data.objects import Objects
from data.users import User
from data.Courses import Course
from Errors import BadCourse, Badlesson
from gregorian_calendar import GregorianCalendar
from help_function import all_courses, all_lessons, all_tasks, calendar_name, \
    chang_course, creation_course, creation_lesson, get_lesson_name_by_id, \
    get_lesson_names_by_object, get_lessons_by_course, \
    get_task_names_by_object, is_teacher, students_for_teacher

my_super_app = Flask(__name__)
my_super_app.config.from_object("config")
my_super_app.config['SECRET_KEY'] = '12Wqfgr66ThSd88UI234901_qprjf'
api = Api(my_super_app)

db_session.global_init("db/main.db")

login_manager = LoginManager()
login_manager.init_app(my_super_app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class TeacherRegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class StudentRegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    grade = SelectField('Класс', choices=[5, 6, 7, 8, 9, 10, 11])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewCourseForm(FlaskForm):
    text_name = StringField('Название курса', validators=[DataRequired()])
    db_sess = db_session.create_session()
    objects = db_sess.query(Objects).all()
    object = SelectField('Предмет', choices=[i.name for i in objects])


class NewLessonForm(FlaskForm):
    text_name = StringField('Название урока', validators=[DataRequired()])

    def __init__(self, courses=None, **kwargs):
        super().__init__(**kwargs)
        if courses is None:
            courses = []
        self.object = SelectField('Курс', choices=[i.name for i in courses])


@my_super_app.route('/')
def start():
    return render_template('index.html', title='SuperKsigma')


@my_super_app.route('/reqister_student', methods=['GET', 'POST'])
def register_student():
    form = StudentRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_student.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_student.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.grade = form.grade.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
    return render_template('register_student.html', title='Регистрация',
                           form=form)


@my_super_app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    form = TeacherRegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_teacher.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_teacher.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.is_teacher = True
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_teacher.html', title='Регистрация',
                           form=form)


@my_super_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if user.is_teacher:
                return redirect('/teacher_profile')
            else:
                return redirect('/student_profile')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@my_super_app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect('/login')
    logout_user()
    return redirect('/')


@my_super_app.route('/student_profile')
def cabinet():
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    return render_template('student_cabinet.html', title='Личный кабинет')


@my_super_app.route('/teacher_profile')
def teacher_cabinet():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    return render_template('teacher_cabinet.html', title='Личный кабинет')


@my_super_app.route('/all_courses', methods=['POST', 'GET'])
def all_courses():
    sorting = 'Все'
    if request.method == 'POST':
        sorting = request.form['filter']
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    db_sess = db_session.create_session()
    objects = db_sess.query(Objects).all()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if sorting not in [obj.name for obj in objects] and 'Все' != sorting:
        abort(404)
    if 'Все' == sorting:
        obj = {'name': 'Все'}
        courses = user.courses
    else:
        obj = [obj for obj in objects if obj.name == sorting][0]
        courses = [curs for curs in user.courses if curs.object == obj]
    objects.append({'name': 'Все'})
    return render_template('all_courses.html', title='Все курсы',
                           courses=courses, objects=objects,
                           object_now=obj)


@my_super_app.route('/course/<int:course_id>/')
def course_lessons(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    course_obj = [curs for curs in user.courses if
                  curs.id == course_id]
    if not course_obj:
        abort(404)
    course_obj = db_sess.query(Course).filter(Course.id == course_id).first()
    return render_template('course.html', title='Уроки курса',
                           lessons=course_obj.lessons)


@my_super_app.route('/pass_task/<int:task_id>/', methods=['POST', 'GET'])
def pass_task(task_id):
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')

    q = False
    lesson_obj = db_sess.query(Lesson).filter(Lesson.id == task_id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    for course_obj in user.courses:
        if lesson_obj in course_obj.lessons:
            q = True
    if not q:
        abort(404)
    if not lesson_obj:
        abort(404)

    if request.method == 'POST':
        errors = []
        correct = []
        for task in lesson_obj.tasks:
            if request.form[f'task_{task.id}'].lower() == task.answers.lower():
                correct.append(task)
            else:
                errors.append(task)
        return ' '.join([i.question for i in errors])

    return render_template('pass_task.html', title='Прохождение задачи',
                           lesson=lesson_obj)


@my_super_app.route('/create_course', methods=['POST', 'GET'])
def create_Course():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    form = NewCourseForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        course_obj = Course()
        course_obj.name = form.text_name.data
        object_obj = db_sess.query(Objects).filter(
            Objects.name == form.object.data).first()
        course_obj.object_id = object_obj.id
        db_sess.add(course_obj)
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.courses.append(course_obj)
        db_sess.commit()
        return redirect('teacher_profile')

    return render_template('create_course.html', title='Создание курса',
                           form=form)


@my_super_app.route('/create_lesson', methods=['POST', 'GET'])
def create_lesson():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if not user.courses:
        return 'У вас ещё нет курсов'

    form = NewLessonForm(user.courses)
    if form.validate_on_submit():
        lessons = []
        for i in range(10):
            if request.form[f'task_{i}'] and request.form[f'answer_{i}']:
                lessons.append((request.form[f'task_{i}'],
                                request.form[f'answer_{i}']))
        if not lessons:
            return render_template('create_lesson.html',
                                   title='Создание урока',
                                   form=form,
                                   error='Нет правильно заполненных задач')
        print(lessons)

        return redirect('teacher_profile')

    return render_template('create_lesson.html', title='Создание урока',
                           form=form)


@my_super_app.route('/teacher_calendar/')
@login_required
def teacher_calendar():
    if is_teacher(current_user.get_id()):
        calendar_title = calendar_name('Ivan')
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
                               title='Личный кабинет',
                               calendar_id=calendar_title,
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
                               students=students)
    else:
        abort(404)


@my_super_app.route('/teacher/tasks', methods=['POST', 'GET'])
@login_required
def tasks():
    if is_teacher(current_user.get_id()):
        if request.method == 'GET':
            return render_template('teach_create_task.html',
                                   title='Создание задачи')
        elif request.method == 'POST':
            print(request.form.get('text'))
            print(request.form.get('lesson'))
            print(request.form.get('file'))
            return redirect('/teacher/check_tasks')
    else:
        abort(404)


@my_super_app.route('/teacher/check_tasks', methods=['POST'])
@login_required
def check_tasks():
    TEMPLATE = 'teach_check.html'
    files = request.files['file'].read().decode('utf-8-sig')
    files_s = [i.strip() for i in files.split('\n')]
    file = {}
    for i in files_s:
        if i:
            file[i.split(':')[0]] = [j.strip() for j in
                                     i.split(':')[1].split('|')]
    file_lines = []
    error = None
    if file['Type'][0] == 'close':
        for i in range(len(file['Questions'])):
            if i == len(file['Answers']):
                file_lines = []
                error = 'Ошибка, ответов меньше чем вопросов'
                break
            else:
                file_lines.append(
                    file['Questions'][i] + ': ' + file['Answers'][i] + '\n')
        context = {'title': 'Проверка задачи',
                   'file_lines': file_lines,
                   'error': error
                   }
        return render_template(TEMPLATE, **context)
    elif file['Type'][0] == 'open':
        for i in range(len(file['Questions'])):
            if i == len(file['Variations_of_answers']):
                file_lines = []
                error = 'Ошибка, ответов меньше чем вопросов'
                break
            else:
                file_lines.append({'question': file['Questions'][i] + '\n',
                                   'answers': [i + '\n' for i in
                                               file['Variations_of_answers'][
                                                   i].split(', ')]
                                   })

        context = {'title': 'Проверка задачи',
                   'file_lines': file_lines,
                   'check_box': True,
                   'error': error
                   }
        return render_template(TEMPLATE, **context)


@my_super_app.route('/<calendar_id>/<year>/<month>/new_task',
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


@my_super_app.route('/<calendar_id>/<year>/<month>/<day>/<task_id>/',
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


@my_super_app.route('/calendar_student')
def student_calendar_1():
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


@my_super_app.route('/lesson', methods=['POST'])
def lesson():
    lst = request.form.get('array').split(',')
    name = request.form.get('name')
    try:
        creation_lesson(lst, name)
    except Badlesson:
        return jsonify({'sucess': 'bad'})
    return jsonify({'succes': 'Ok'})


@my_super_app.route('/create_courses/<filter_name>/', methods=["GET", "POST"])
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


@my_super_app.route('/course', methods=['POST'])
def course():
    lst = request.form.get('array').split(',')
    name = request.form.get('name')
    try:
        creation_course(lst, name)
    except BadCourse:
        return jsonify({'sucess': 'bad'})
    return jsonify({'succes': 'Ok'})


@my_super_app.route('/change_course/<filter_name>/')
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
                                course_now=filter_name, form=form,
                                courses=courses))
    else:
        lessons_cr = get_lessons_by_course(filter_name)
        lessons_cr = [get_lesson_name_by_id(i) for i in lessons_cr]
        print(lessons_cr)
        return render_template('change_courses.html', title='Создание курсов',
                               lessons=lessons,
                               objects=['math', 'russia'],
                               base_url=current_app.config["BASE_URL"],
                               course_now=filter_name, form=form,
                               courses=courses, lessons_cr=lessons_cr)


@my_super_app.route('/help_filter/<filter_name>/', methods=['POST'])
def help_lesson(filter_name):
    lst = get_lesson_names_by_object(filter_name)
    return jsonify({'lst': lst})


@my_super_app.route('/changing_course', methods=['POST'])
def changing_course():
    lst = request.form.get('array').split(',')
    name = request.form.get('name')
    try:
        chang_course(lst, name)
    except BadCourse:
        return jsonify({'sucess': 'bad'})
    return jsonify({'succes': 'Ok'})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    api.add_resource(task_resource.Task, '/<calendar_id>/new_task')
    my_super_app.run(host='127.0.0.1', port=port)
