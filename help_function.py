from data.calendar import CalendarDB
from data.db_session import global_init, create_session


def calendar_name(user_id):
    """возвращает название календаря, соответствующего айди ученика"""
    print(user_id)
    db_sess = connect_to_db('users.db')
    for calendar in (db_sess.query(CalendarDB).filter(CalendarDB.student_id == user_id)):
        if calendar.calendar_name == None: # заглушка потом переделается на вывод у Вас еще нет расписания
            return 'calendar.json'




def connect_to_db(name_bd):
    """подключается к базе данных"""
    global_init(name_bd)
    return create_session()
