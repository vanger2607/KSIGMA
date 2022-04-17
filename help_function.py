from Errors import Badlesson, BadCourse
from data.Courses import Course
from data.calendar import CalendarDB
from data.db_session import global_init, create_session
from data.lesson import Lesson
from data.objects import Objects
from data.tasks import SuperTasks
from data.teachers import Teacher
from data.users import User


def calendar_name(user_id):
    """возвращает название календаря, соответствующего айди ученика"""
    print(user_id)
    db_sess = connect_to_db('users.db')
    for calendar in (db_sess.query(CalendarDB).filter(CalendarDB.student_id == user_id)):
        return calendar.calendar_name


def connect_to_db(name_bd):
    """подключается к базе данных"""
    global_init(name_bd)
    return create_session()


def students_for_teacher(teacher_id):
    """возвращает список учеников определенного учителя"""
    db_sess = connect_to_db('users.db')
    names = []
    for teacher in (db_sess.query(Teacher).filter(Teacher.id == teacher_id)):
        lst_of_students = teacher.students.split(', ')
        for i in lst_of_students:
            for student in (db_sess.query(User).filter(User.id == int(i))):
                names.append(student.name)

        return names


def get_student_id(name):
    """по никнейму пользователя возвращает его айди"""
    db_sess = connect_to_db('users.db')
    for user in (db_sess.query(User).filter(User.name == name)):
        return user.id


def get_task_id(task):
    """по имени возвращает id задания"""
    db_sess = connect_to_db('users.db')
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task)):
        return task.id


def get_info_about_task(task):
    """по названию задания возвращает вопросы и тип задания"""
    db_sess = connect_to_db('users.db')
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task)):
        print(task.type, task.question)
        return [task.type, task.question]


def all_tasks():
    """возвращает список названий всех задач"""
    tasks = []
    db_sess = connect_to_db('users.db')
    for task in (db_sess.query(SuperTasks)).all():
        tasks.append(task.name)
    return tasks


def all_lessons():
    """возвращает список названий всех уроков"""
    lessons = []
    db_sess = connect_to_db('users.db')
    for lesson in (db_sess.query(Lesson)).all():
        lessons.append(lesson.name)
    return lessons


def all_courses():
    """возвращает список названий всех курсов"""
    courses = []
    db_sess = connect_to_db('users.db')
    for course in (db_sess.query(Course)).all():
        courses.append(course.name)
    return courses


def get_task_names_by_object(object_name):
    """по предмету(школьному) возвращает список задач"""
    db_sess = connect_to_db('users.db')
    tasks = []
    object_id = get_object_id_by_name(object_name)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.type_object == object_id)):
        tasks.append(task.name)
    return tasks


def get_lesson_names_by_object(object_name):
    """по школьному предмету возвращает список уроков"""
    db_sess = connect_to_db('users.db')
    lessons = []
    object_id = get_object_id_by_name(object_name)
    for lesson in (db_sess.query(Lesson).filter(Lesson.type_object == object_id)):
        lessons.append(lesson.name)
    return lessons


def get_lesson_id(lesson_name):
    """по имени возвращает id урока"""
    db_sess = connect_to_db('users.db')
    for lesson in (db_sess.query(Lesson).filter(Lesson.name == lesson_name)):
        return lesson.id


def creation_lesson(tasks, name):
    """добавляет урок в таблицу lessons"""
    db_sess = connect_to_db('users.db')
    lesson = Lesson()
    tasks_id = []
    for i in tasks:
        tasks_id.append(str(get_task_id(i)))
    if is_all_tasks_one_type(tasks):
        lesson.tasks = ', '.join(tasks_id)
        lesson.name = name
        tp_object = get_object_by_task_name(tasks[0])
        lesson.type_object = tp_object
        db_sess.add(lesson)
        db_sess.commit()
    else:
        raise Badlesson


def is_all_lessons_one_type(lessons):
    """проверяет все ли задачи в уроке одного школьного предмета"""
    first_type = get_object_by_lesson_name(lessons[0])
    for i in lessons:
        if get_object_by_lesson_name(i) != first_type:
            return False
    return True


def creation_course(lessons, name):
    """добавляет курс в таблицу courses"""
    db_sess = connect_to_db('users.db')
    course = Course()
    lessons_id = []
    for i in lessons:
        lessons_id.append(str(get_lesson_id(i)))
    if is_all_lessons_one_type(lessons):
        course.lessons = ', '.join(lessons_id)
        course.name = name
        tp_object = get_object_by_lesson_name(lessons[0])
        course.object = tp_object
        db_sess.add(course)
        db_sess.commit()
    else:
        raise BadCourse


def chang_course(lessons, name):
    """изменение курса(удаляет, добавляет айди уроков)"""
    db_sess = connect_to_db('users.db')
    for course in (db_sess.query(Course).filter(Course.name == name)):
        cours = course
    lessons_id = []
    for i in lessons:
        lessons_id.append(str(get_lesson_id(i)))
    if is_all_lessons_one_type(lessons):
        cours.lessons = ', '.join(lessons_id)
        tp_object = get_object_by_lesson_name(lessons[0])
        cours.object = tp_object
        db_sess.commit()
    else:
        raise BadCourse
def get_object_by_task_name(task_name):
    """возвращает айди объекта по названию задания"""
    db_sess = connect_to_db('users.db')
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task_name)):
        return task.type_object


def get_object_by_lesson_name(lesson_name):
    """возвращает айди объекта по названию урока"""
    db_sess = connect_to_db('users.db')
    for lesson in (db_sess.query(Lesson).filter(Lesson.name == lesson_name)):
        return lesson.type_object


def is_all_tasks_one_type(tasks):
    """проверяет все ли задачи в уроке одного школьного предмета"""
    first_type = get_object_by_task_name(tasks[0])
    for i in tasks:
        if get_object_by_task_name(i) != first_type:
            return False
    return True


def get_object_id_by_name(object_name: str):
    """возвращает айди школьно предмета по его названию"""
    db_sess = connect_to_db('users.db')
    for object_ in (db_sess.query(Objects).filter(Objects.name == object_name.capitalize())).all():
        return object_.id


def get_calendar_id_by_name(calendar_nm):
    """возвращает айди календаря, по его названию"""
    db_sess = connect_to_db('users.db')
    for calendar in (db_sess.query(CalendarDB).filter(CalendarDB.calendar_name == calendar_nm)):
        return calendar.student_id


def get_student_name_by_id(student_id):
    """возвращает никнейм ученика по его айди"""
    db_sess = connect_to_db('users.db')
    for user in (db_sess.query(User).filter(User.id == student_id)):
        return user.name


def is_teacher(user_id):
    """по айди пользователя возвращает является ли он учителем(False или True)"""
    db_sess = connect_to_db('users.db')
    for user in (db_sess.query(User).filter(User.id == user_id)):
        return user.is_teacher == 1


def get_lessons_by_course(course_name):
    """по названию курса возвращает айди всех уроков"""
    db_sess = connect_to_db('users.db')
    for course in (db_sess.query(Course).filter(Course.name == course_name)):
        return course.lessons.split(', ')


def get_lesson_name_by_id(lesson_id: str):
    """возвращает название урока по его айди"""
    db_sess = connect_to_db('users.db')
    for lesson in (db_sess.query(Lesson).filter(Lesson.id == lesson_id)):
        return lesson.name