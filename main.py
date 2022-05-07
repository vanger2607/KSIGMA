import os
from json import dumps, loads

from flask import Flask, redirect, \
    render_template, request
from flask_login import current_user, login_user, LoginManager, logout_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, \
    SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

from data import db_session
from data.Courses import Course
from data.lesson import Lesson
from data.objects import Objects
from data.results import Result
from data.tasks import SuperTasks
from data.users import User

my_super_app = Flask(__name__)
my_super_app.config['SECRET_KEY'] = '12Wqfgr66ThSd88UI234901_qprjf'

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


class TeacherUpdateForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class StudentRegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    grade = SelectField('Класс', choices=[5, 6, 7, 8, 9, 10, 11])
    submit = SubmitField('Зарегистрироваться')


class StudentUpdateForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    grade = SelectField('Класс', choices=[5, 6, 7, 8, 9, 10, 11])
    submit = SubmitField('Изменить')


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


class UpdateCourseForm(FlaskForm):
    text_name = StringField('Новое название курса',
                            validators=[DataRequired()])
    db_sess = db_session.create_session()
    objects = db_sess.query(Objects).all()
    object = SelectField('Новый предмет', choices=[i.name for i in objects])


class NewLessonForm(FlaskForm):
    text_name = StringField('Название урока', validators=[DataRequired()])


class UpdateLessonForm(FlaskForm):
    text_name = StringField('Название урока', validators=[DataRequired()])


@my_super_app.route('/')
def start():
    return render_template('index.html', title='КСИГМА')


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
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('teacher_cabinet.html', title='Личный кабинет',
                           user=user)


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
        return redirect('/teacher_profile')
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
        return redirect('/student_profile')
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
        return redirect('/student_profile')
    if not lesson_obj:
        return redirect('/student_profile')

    if request.method == 'POST':
        errors = []
        correct = 0
        for task in lesson_obj.tasks:
            if request.form[f'task_{task.id}'].lower().strip() \
                    != task.answers.lower().strip():
                errors.append((task.question, task.answers.strip(),
                               request.form[f'task_{task.id}'].lower()))
            else:
                correct += 1
        result_dict = {'mark': f'{correct}/{len(lesson_obj.tasks)}',
                       'errors': errors}
        result_obj = Result()
        result_obj.test = dumps(result_dict)
        result_obj.user_id = user.id
        result_obj.lesson_id = lesson_obj.id
        db_sess.add(result_obj)
        db_sess.commit()
        return render_template('pass_task_complete.html',
                               title='Прохождение задачи завершено',
                               result_dict=result_dict)

    return render_template('pass_task.html', title='Прохождение задачи',
                           lesson=lesson_obj, form=FlaskForm())


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
        return redirect('/teacher_profile')

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

    form = NewLessonForm()
    if form.validate_on_submit():
        courses_obj = db_sess.query(Course).filter(
            Course.id == int(request.form[f'courses'].split('_')[-1])).first()
        tasks_list = []
        for i in range(10):
            if request.form[f'task_{i}'] and request.form[f'answer_{i}']:
                tasks_list.append((request.form[f'task_{i}'],
                                   request.form[f'answer_{i}']))
        if not tasks_list:
            return render_template('create_lesson.html',
                                   title='Создание урока',
                                   form=form,
                                   error='Нет правильно заполненных задач',
                                   courses=user.courses)
        less = Lesson()
        less.name = form.text_name.data
        less.type_object = courses_obj.object_id
        db_sess.add(less)
        courses_obj.lessons.append(less)
        db_sess.commit()
        db_sess = db_session.create_session()

        less_obj = db_sess.query(Lesson).filter(
            Lesson.name == str(form.text_name.data) and
            Lesson.type_object == courses_obj.object_id
        ).first()
        for task in tasks_list:
            task_obj = SuperTasks()
            task_obj.type = 'input'
            task_obj.question = task[0].strip()
            task_obj.answers = task[1].strip()
            task_obj.lesson_id = less_obj.id
            db_sess.add(task_obj)
        db_sess.commit()
        return redirect('/teacher_profile')

    return render_template('create_lesson.html', title='Создание урока',
                           form=form, courses=user.courses)


@my_super_app.route('/teacher_students_add', methods=['POST', 'GET'])
def teacher_students_add():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    your_students = list(map(int, current_user.student_ids.split()))
    students = db_sess.query(User).filter(User.id != current_user.id).filter(
        User.is_teacher.is_(False)).all()
    students = [student_obj for student_obj in students if
                student_obj.id not in your_students]

    if request.method == 'POST':
        for field in request.form:
            your_students.append(str(field).split('_')[1])
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.student_ids = ' '.join(map(str, your_students))
        db_sess.commit()
        return redirect('/teacher_profile')

    return render_template('teacher_students_add.html', title='Выбор учеников',
                           students=students, form=FlaskForm())


@my_super_app.route('/teacher_students', methods=['POST', 'GET'])
def teacher_students():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    your_students = list(map(int, current_user.student_ids.split()))
    students = db_sess.query(User).filter(User.id != current_user.id).filter(
        User.is_teacher.is_(False)).all()
    students = [student_obj for student_obj in students if
                student_obj.id in your_students]

    if request.method == 'POST':
        for i in request.form:
            your_students.remove(int(str(i).split('_')[1]))
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.student_ids = ' '.join(map(str, your_students))
        db_sess.commit()
        return redirect('/teacher_profile')

    return render_template('teacher_students.html', title='Ваши ученики',
                           students=students, form=FlaskForm())


@my_super_app.route('/teacher_students_add_course', methods=['POST', 'GET'])
def teacher_students_add_course():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    your_students = list(map(int, current_user.student_ids.split()))
    students = db_sess.query(User).filter(User.id != current_user.id).filter(
        User.is_teacher.is_(False)).all()
    students = [student_obj for student_obj in students if
                student_obj.id in your_students]

    if request.method == 'POST':
        courses_obj = db_sess.query(Course).filter(
            Course.id == int(request.form[f'course'].split('_')[-1])).first()
        for field in request.form:
            if field.startswith('student'):
                student_obj = db_sess.query(User).filter(
                    User.id == int(field.split('_')[-1])).first()
                if courses_obj not in student_obj.courses:
                    student_obj.courses.append(courses_obj)
        db_sess.commit()
        return redirect('/teacher_profile')

    return render_template('teacher_students_add_course.html',
                           title='Выдать курс',
                           students=students,
                           courses=user.courses,
                           form=FlaskForm())


@my_super_app.route('/teacher_students_remove_course', methods=['POST', 'GET'])
def teacher_students_remove_course():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    your_students = list(map(int, current_user.student_ids.split()))
    students = db_sess.query(User).filter(User.id != current_user.id).filter(
        User.is_teacher.is_(False)).all()
    students = [student_obj for student_obj in students if
                student_obj.id in your_students]
    courses_dict = {}
    for student_obj in students:
        for course in student_obj.courses:
            if course in courses_dict:
                courses_dict[course].append(student_obj)
            else:
                courses_dict[course] = [student_obj]

    if request.method == 'POST':
        for field in request.form:
            student_obj = db_sess.query(User).filter(
                User.id == int(field.split('_')[-1])).first()
            student_obj.courses.remove(db_sess.query(Course).filter(
                Course.id == int(field.split('_')[0])).first())
        db_sess.commit()
        return redirect('/teacher_profile')

    return render_template('teacher_students_remove_course.html',
                           title='Забрать курс',
                           courses_dict=courses_dict,
                           form=FlaskForm())


@my_super_app.route('/change_courses/')
def change_courses():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('change_courses.html',
                           title='Выбор курса для редактирования',
                           courses=user.courses)


@my_super_app.route('/change_lessons_courses/')
def change_lessons_courses():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('change_lessons_courses.html',
                           title='Выбор курса для редактирования',
                           courses=user.courses)


@my_super_app.route('/change_lessons_course/<int:course_id>/')
def change_lessons_course(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    course_obj = db_sess.query(Course).filter(Course.id == course_id).first()
    if not course_obj:
        return redirect('/student_profile')
    return render_template('change_lessons_course.html',
                           title='Выбор урока для редактирования',
                           lessons=course_obj.lessons)


@my_super_app.route('/change_course/<int:course_id>/', methods=['POST', 'GET'])
def change_course(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    course_obj = db_sess.query(Course).filter(Course.id == course_id).first()
    if not course_obj:
        return redirect('/student_profile')
    form = UpdateCourseForm(object=course_obj.object.name)
    if form.validate_on_submit():
        course_obj.name = form.text_name.data
        object_obj = db_sess.query(Objects).filter(
            Objects.name == form.object.data).first()
        course_obj.object_id = object_obj.id
        db_sess.commit()
        return redirect('/teacher_profile')

    return render_template('change_course.html', title='Редактирование курса',
                           form=form, course=course_obj)


@my_super_app.route('/change_lesson/<int:lesson_id>/', methods=['POST', 'GET'])
def change_lesson(lesson_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    lesson_obj = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if not lesson_obj:
        return redirect('/student_profile')
    form = UpdateLessonForm()
    if form.validate_on_submit():
        courses_obj = db_sess.query(Course).filter(
            Course.id == int(request.form[f'courses'].split('_')[-1])).first()
        new_tasks_list = []
        for i in range(10 - len(lesson_obj.tasks)):
            if request.form[f'task_{i}'] and request.form[f'answer_{i}']:
                new_tasks_list.append((request.form[f'task_{i}'],
                                       request.form[f'answer_{i}']))

        old_tasks_list = []
        for i in [task.id for task in lesson_obj.tasks]:
            if request.form[f'old_task_{i}'] and \
                    request.form[f'old_answer_{i}']:
                old_tasks_list.append((i, request.form[f'old_task_{i}'],
                                       request.form[f'old_answer_{i}']))
        if not new_tasks_list and not old_tasks_list:
            return render_template('change_lesson.html',
                                   title='Редактирование урока',
                                   form=form,
                                   error='Нет правильно заполненных задач',
                                   lesson=lesson_obj,
                                   courses=user.courses)

        lesson_obj.name = form.text_name.data
        if lesson_obj.course_id != courses_obj.id:
            old_courses_obj = db_sess.query(Course).filter(
                Course.id == lesson_obj.course_id).first()
            old_courses_obj.lessons.remove(lesson_obj)
            courses_obj.lessons.append(lesson_obj)

        for task in new_tasks_list:
            task_obj = SuperTasks()
            task_obj.type = 'input'
            task_obj.question = task[0].strip()
            task_obj.answers = task[1].strip()
            task_obj.lesson_id = lesson_obj.id
            db_sess.add(task_obj)

        for task in old_tasks_list:
            task_obj = db_sess.query(SuperTasks).filter(
                SuperTasks.id == task[0]).first()
            task_obj.type = 'input'
            task_obj.question = task[1].strip()
            task_obj.answers = task[2].strip()
            db_sess.add(task_obj)

        db_sess.commit()
        return redirect('/teacher_profile')

    return render_template('change_lesson.html', title='Редактирование урока',
                           form=form, lesson=lesson_obj, courses=user.courses)


@my_super_app.route('/all_results_courses/')
def all_results_courses():
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('all_results_courses.html',
                           title='Выбор курса для просмотра результатов',
                           courses=user.courses)


@my_super_app.route('/all_results_lessons/<int:course_id>/')
def all_results_lessons(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    db_sess = db_session.create_session()
    course_obj = db_sess.query(Course).filter(Course.id == course_id).first()
    if not course_obj:
        return redirect('/student_profile')
    return render_template('all_results_lessons.html',
                           title='Выбор урока для просмотра результатов',
                           lessons=course_obj.lessons)


@my_super_app.route('/all_results_lesson/<int:lesson_id>/')
def all_results_lesson(lesson_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    db_sess = db_session.create_session()
    lesson_obj = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson_obj:
        return redirect('/student_profile')
    results = db_sess.query(Result).filter(
        Result.lesson_id == lesson_id and Result.user_id == current_user.id)
    return render_template('all_results_lesson.html',
                           title='Ваши результаты',
                           lesson=lesson_obj,
                           results=[loads(i.test) for i in results.all()])


@my_super_app.route('/all_results_courses_teacher/')
def all_results_courses_teacher():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('all_results_courses_teacher.html',
                           title='Выбор курса для просмотра' +
                                 ' результатов учеников',
                           courses=user.courses)


@my_super_app.route('/all_results_lessons_teacher/<int:course_id>/')
def all_results_lessons_teacher(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    course_obj = db_sess.query(Course).filter(Course.id == course_id).first()
    if not course_obj:
        return redirect('/student_profile')
    return render_template('all_results_lessons_teacher.html',
                           title='Выбор урока для просмотра результатов' +
                                 ' учеников',
                           lessons=course_obj.lessons)


@my_super_app.route('/all_results_lesson_teacher/<int:lesson_id>/')
def all_results_lesson_teacher(lesson_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    lesson_obj = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson_obj:
        return redirect('/teacher_profile')
    results_dict = {}
    for result in lesson_obj.results:
        if result.user.name in results_dict:
            results_dict[result.user.name].append(loads(result.test)['mark'])
        else:
            results_dict[result.user.name] = [loads(result.test)['mark']]
    return render_template('all_results_lesson_teacher.html',
                           title='Результаты ваших учеников',
                           lesson=lesson_obj,
                           results_dict=results_dict)


@my_super_app.route('/my_teachers')
def my_teachers():
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    teachers = []
    db_sess = db_session.create_session()
    all_teachers = db_sess.query(User).filter(User.is_teacher.is_(True)).all()
    for teacher in all_teachers:
        if str(current_user.id) in teacher.student_ids:
            teachers.append(teacher)
    return render_template('my_teachers.html',
                           title='Мои учителя', teachers=teachers)


@my_super_app.route('/update_student_profile', methods=['POST', 'GET'])
def update_student_profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    if current_user.is_teacher:
        return redirect('/teacher_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    form = StudentUpdateForm(
        email=user.email,
        name=user.name,
        surname=user.surname,
        grade=user.grade,
    )
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.email == form.email.data).filter(
                User.id != user.id).first():
            return render_template('update_student_profile.html',
                                   title='Изменеие данных',
                                   form=form,
                                   message="Пользователь с таким email" +
                                           " уже есть")
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.grade = form.grade.data
        db_sess.commit()

        return redirect('/student_profile')
    return render_template('update_student_profile.html',
                           title='Изменеие данных',
                           form=form)


@my_super_app.route('/update_teacher_profile', methods=['POST', 'GET'])
def update_teacher_profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.is_teacher:
        return redirect('/student_profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    form = TeacherUpdateForm(
        email=user.email,
        name=user.name,
        surname=user.surname,
    )
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.email == form.email.data).filter(
                User.id != user.id).first():
            return render_template('update_student_profile.html',
                                   title='Изменеие данных',
                                   form=form,
                                   message="Пользователь с таким email" +
                                           " уже есть")
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        db_sess.commit()

        return redirect('/teacher_profile')
    return render_template('update_teacher_profile.html',
                           title='Изменеие данных',
                           form=form)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    my_super_app.run(host='127.0.0.1', port=port)
