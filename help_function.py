from data.calendar import CalendarDB
from data.db_session import global_init, create_session
from data.lesson import Lesson
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
    db_sess = connect_to_db('users.db')
    for user in (db_sess.query(User).filter(User.name == name)):
        return user.id

def get_task_id(task):
    """по имени возвращает id задания"""
    db_sess =connect_to_db('users.db')
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task)):
        return task.id
def get_info_about_task(task):
    """по названию задания возвращает вопросы и тип задания"""
    db_sess = connect_to_db('users.db')
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task)):
        print(task.type, task.question)
        return [task.type, task.question]


def get_task_name_by_object(object):
    """по предмету(школьного) возвращает список задач"""
    db_sess = connect_to_db('users.db')
    tasks = []
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.type_object == object)):
        tasks.append(task.name)
    return tasks


def all_tasks():
    """возвращает список названий всех задач"""
    tasks = []
    db_sess = connect_to_db('users.db')
    for task in (db_sess.query(SuperTasks)).all():
        tasks.append(task.name)
    return tasks


def append_tasks_to_lesson(tasks):
    """добавляет айди задач в ячейку tasks таблицы lessons"""
    db_sess = connect_to_db('users.db')
    lesson = Lesson()
    tasks_id = []
    for i in tasks:
        tasks_id.append(str(get_task_id(i)))

    lesson.tasks = ', '.join(tasks_id)
    db_sess.add(lesson)
    db_sess.commit()
