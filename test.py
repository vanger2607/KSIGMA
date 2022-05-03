from data import db_session, task_resource
from data.lesson import Lesson
from data.tasks import SuperTasks
from data.objects import Objects
from data.Courses import Course


db_session.global_init("db/main.db")

db_sess = db_session.create_session()

cours = Course()
cours.name = 'Простая математика'
cours.type_object = db_sess.query(Objects).filter(Objects.name == 'Match').first().id
cours.lessons = [db_sess.query(Lesson).first()]
db_sess.add(cours)

db_sess.commit()
