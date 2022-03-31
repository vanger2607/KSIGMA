from data.calendar import CalendarDB
from data.db_session import global_init, create_session
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
