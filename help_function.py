import config
from Errors import Badlesson, BadCourse
from data.Courses import Course
from data.calendar import CalendarDB
from data.db_session import global_init, create_session
from data.lesson import Lesson
from data.objects import Objects
from data.tasks import SuperTasks
from data.teachers import Teacher
from data.users import User


def calendar_name(user_id: int):
    """возвращает название календаря, соответствующего айди ученика"""
    print(user_id)
    db_sess = connect_to_db(config.DB_NAME)
    for calendar in (db_sess.query(CalendarDB).filter(CalendarDB.student_id == user_id)):
        return calendar.calendar_name


def connect_to_db(name_bd: str):
    """подключается к базе данных"""
    global_init(name_bd)
    return create_session()


def students_for_teacher(teacher_id: int):
    """возвращает список учеников определенного учителя"""
    db_sess = connect_to_db(config.DB_NAME)
    names = []
    for teacher in (db_sess.query(Teacher).filter(Teacher.id == teacher_id)):
        lst_of_students = teacher.students.split(', ')
        for i in lst_of_students:
            for student in (db_sess.query(User).filter(User.id == int(i))):
                names.append(student.name)

        return names


def get_student_id(name: str):
    """по никнейму пользователя возвращает его айди"""
    db_sess = connect_to_db(config.DB_NAME)
    for user in (db_sess.query(User).filter(User.name == name)):
        return user.id


def get_task_id(task: str):
    """по имени возвращает id задания"""
    db_sess = connect_to_db(config.DB_NAME)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task)):
        return task.id


def get_info_about_task(task: str):
    """по названию задания возвращает вопросы и тип задания"""
    db_sess = connect_to_db(config.DB_NAME)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task)):
        print(task.type, task.question)
        return [task.type, task.question]


def all_tasks():
    """возвращает список названий всех задач"""
    tasks = []
    db_sess = connect_to_db(config.DB_NAME)
    for task in (db_sess.query(SuperTasks)).all():
        tasks.append(task.name)
    return tasks


def all_lessons():
    """возвращает список названий всех уроков"""
    lessons = []
    db_sess = connect_to_db(config.DB_NAME)
    for lesson in (db_sess.query(Lesson)).all():
        lessons.append(lesson.name)
    return lessons


def all_courses():
    """возвращает список названий всех курсов"""
    courses = []
    db_sess = connect_to_db(config.DB_NAME)
    for course in (db_sess.query(Course)).all():
        courses.append(course.name)
    return courses


def get_task_names_by_object(object_name: str):
    """по предмету(школьному) возвращает список задач"""
    db_sess = connect_to_db(config.DB_NAME)
    tasks = []
    object_id = get_object_id_by_name(object_name)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.type_object == object_id)):
        tasks.append(task.name)
    return tasks


def get_lesson_names_by_object(object_name: str):
    """по школьному предмету возвращает список уроков"""
    db_sess = connect_to_db(config.DB_NAME)
    lessons = []
    object_id = get_object_id_by_name(object_name)
    for lesson in (db_sess.query(Lesson).filter(Lesson.type_object == object_id)):
        lessons.append(lesson.name)
    return lessons


def get_lesson_id(lesson_name: str):
    """по имени возвращает id урока"""
    db_sess = connect_to_db(config.DB_NAME)
    for lesson in (db_sess.query(Lesson).filter(Lesson.name == lesson_name)):
        return lesson.id


def creation_lesson(tasks: list, name : str):
    """добавляет урок в таблицу lessons"""
    db_sess = connect_to_db(config.DB_NAME)
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


def is_all_lessons_one_type(lessons: list):
    """проверяет все ли задачи в уроке одного школьного предмета"""
    first_type = get_object_by_lesson_name(lessons[0])
    for i in lessons:
        if get_object_by_lesson_name(i) != first_type:
            return False
    return True


def creation_course(lessons: list, name: str):
    """добавляет курс в таблицу courses"""
    db_sess = connect_to_db(config.DB_NAME)
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


def chang_course(lessons: list, name: str):
    """изменение курса(удаляет, добавляет айди уроков)"""
    db_sess = connect_to_db(config.DB_NAME)
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


def get_object_by_task_name(task_name: str):
    """возвращает айди объекта по названию задания"""
    db_sess = connect_to_db(config.DB_NAME)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.name == task_name)):
        return task.type_object


def get_object_by_lesson_name(lesson_name: str):
    """возвращает айди объекта по названию урока"""
    db_sess = connect_to_db(config.DB_NAME)
    for lesson in (db_sess.query(Lesson).filter(Lesson.name == lesson_name)):
        return lesson.type_object


def is_all_tasks_one_type(tasks: list):
    """проверяет все ли задачи в уроке одного школьного предмета"""
    first_type = get_object_by_task_name(tasks[0])
    for i in tasks:
        if get_object_by_task_name(i) != first_type:
            return False
    return True


def get_object_id_by_name(object_name: str):
    """возвращает айди школьно предмета по его названию"""
    db_sess = connect_to_db(config.DB_NAME)
    for object_ in (db_sess.query(Objects).filter(Objects.name == object_name.capitalize())).all():
        return object_.id


def get_calendar_id_by_name(calendar_nm: str):
    """возвращает айди календаря, по его названию"""
    db_sess = connect_to_db(config.DB_NAME)
    for calendar in (db_sess.query(CalendarDB).filter(CalendarDB.calendar_name == calendar_nm)):
        return calendar.student_id


def get_student_name_by_id(student_id: int):
    """возвращает никнейм ученика по его айди"""
    db_sess = connect_to_db(config.DB_NAME)
    for user in (db_sess.query(User).filter(User.id == student_id)):
        return user.name


def is_teacher(user_id: int):
    """по айди пользователя возвращает является ли он учителем(False или True)"""
    db_sess = connect_to_db(config.DB_NAME)
    for user in (db_sess.query(User).filter(User.id == user_id)):
        return user.is_teacher == 1


def get_lessons_by_course(course_name: str):
    """по названию курса возвращает айди всех уроков"""
    db_sess = connect_to_db(config.DB_NAME)
    for course in (db_sess.query(Course).filter(Course.name == course_name)):
        if len(str(course.lessons)) > 1:
            return course.lessons.split(', ')
        return [course.lessons]


def get_lesson_name_by_id(lesson_id: str):
    """возвращает название урока по его айди"""
    db_sess = connect_to_db(config.DB_NAME)
    for lesson in (db_sess.query(Lesson).filter(Lesson.id == lesson_id)):
        return lesson.name


def get_course_by_subject(subject: str):
    """возвращает названия курсов по названию предмета """
    db_sess = connect_to_db(config.DB_NAME)
    courses = []
    subject_id = get_object_id_by_name(subject)
    for course in (db_sess.query(Course).filter(Course.object == subject_id)):
        courses.append(course.name)
    return courses
def get_type_of_task_by_id(task_id):
    """возвращает тип задачи по ее айди"""
    db_sess = connect_to_db(config.DB_NAME)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.id == task_id)):
        return task.type


def get_info_about_task_by_id(task_id):
    """возвращает всю информацию о задачах(название, вопросы, тип, варианты ответов если есть, ответы)"""
    db_sess = connect_to_db(config.DB_NAME)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.id == task_id)):
        if task.type == 'check-boxes' or task.type == 'radio-buttons':
            return(task.name, task.question, task.type, task.variations_of_answers, task.answers)
        return (task.name, task.question, task.type, task.answers)


def get_name_task_by_id(task_id):
    """по айди задачи возвращает ее название"""
    db_sess = connect_to_db(config.DB_NAME)
    for task in (db_sess.query(SuperTasks).filter(SuperTasks.id == task_id)):
        return task.name


def get_all_task_from_lesson(lesson_name):
    """по названию урока возвращает все задачи входящие в него"""
    db_sess = connect_to_db(config.DB_NAME)
    for lesson in (db_sess.query(Lesson)).filter(Lesson.name == lesson_name):
        tasks = str(lesson.tasks).split(', ')
    return tasks
