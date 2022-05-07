from data import db_session
from data.lesson import Lesson
from data.tasks import SuperTasks
from data.objects import Objects
from data.Courses import Course
from data.users import User

db_session.global_init("db/main.db")

db_sess = db_session.create_session()


obj = Objects()
obj.name = 'Математика'
db_sess.add(obj)
obj = Objects()
obj.name = 'Русский Язык'
db_sess.add(obj)
obj = Objects()
obj.name = 'Геометрия'
db_sess.add(obj)
obj = Objects()
obj.name = 'Python'
db_sess.add(obj)
# less = Lesson()
# less.name = 'Основы математики'
# less.type_object = db_sess.query(Objects).filter(
# Objects.name == 'Match').first().id
# db_sess.add(less)
#
# task = SuperTasks()
# task.type = 'input'
# task.question = '2 + 2?'
# task.answers = '4'
# task.lesson_id = db_sess.query(Lesson).first().id
# db_sess.add(task)
#
# task = SuperTasks()
# task.type = 'input'
# task.question = '2 + 6?'
# task.answers = '8'
# task.lesson_id = db_sess.query(Lesson).first().id
#
# db_sess.add(task)
# task = SuperTasks()
# task.type = 'input'
# task.question = '10 - 5 + 2?'
# task.answers = '7'
# task.lesson_id = db_sess.query(Lesson).first().id
# db_sess.add(task)
#
# cours = Course()
# cours.name = 'Простая математика'
# cours.object_id = db_sess.query(Objects).filter(
# Objects.name == 'Match').first().id
# cours.lessons = [db_sess.query(Lesson).first()]
# db_sess.add(cours)
#
# for i in range(5):
#     user = User()
#     user.name = f"Пользователь {i}"
#     user.email = f"rogozhin-04_{i}@inbox.ru"
#     user.set_password(str(i))
#     db_sess.add(user)

db_sess.commit()
