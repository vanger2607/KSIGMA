class Badlesson(Exception):
    """вызывается если в уроке не у всех задач одинаковое значение type_object"""
    pass
class BadCourse(Exception):
    """вызывается если в курсе не у всех уроков одинаковое значение type_object"""
    pass