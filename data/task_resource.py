import re
from datetime import date, timedelta

from flask import current_app, redirect
from flask_restful import Resource, reqparse

from calendar_data import CalendarData
from help_function import get_calendar_id_by_name, get_student_name_by_id, get_calendar_name_by_id

parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('year')
parser.add_argument('month')
parser.add_argument('day')
parser.add_argument('task_id')
parser.add_argument('date', default='')
parser.add_argument('enddate', default='')
parser.add_argument('is_all_day', default='0')
parser.add_argument('start_time')
parser.add_argument('end_time', default=None)
parser.add_argument('details')
parser.add_argument('color')
parser.add_argument('repeats', default='0')
parser.add_argument('repetition_type')
parser.add_argument('repetition_subtype')
parser.add_argument('repetition_value')


class Task(Resource):
    @staticmethod
    def post(calendar_id):
        args = parser.parse_args()
        title = args["title"].strip()
        startdate = args["date"]
        enddate = args["enddate"]

        if len(startdate) > 0:
            date_fragments = re.split("-", startdate)
            year = int(date_fragments[0])  # type: Optional[int]
            month = int(date_fragments[1])  # type: Optional[int]
            day = int(date_fragments[2])  # type: Optional[int]
        else:
            year = month = day = None
        is_all_day = args["is_all_day"] == "1"
        start_time = args["start_time"]
        end_time = args["end_time"]
        details = args["details"].replace("\r", "").replace("\n", "<br>")
        color = args["color"]
        has_repetition = args["repeats"] == "1"
        repetition_type = args["repetition_type"]
        repetition_subtype = args["repetition_subtype"]
        repetition_value = int(args["repetition_value"])

        calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])

        dates_to_create = []  # type: List[Tuple[Optional[int], Optional[int], Optional[int]]]

        # repetitive tasks not supported
        if startdate != enddate and not has_repetition:
            startdate_fragments = re.split("-", startdate)
            enddate_fragments = re.split("-", enddate)
            sdate = date(int(startdate_fragments[0]), int(startdate_fragments[1]), int(startdate_fragments[2]))
            edate = date(int(enddate_fragments[0]), int(enddate_fragments[1]), int(enddate_fragments[2]))
            delta = edate - sdate
            for i in range(delta.days + 1):
                currentdate = re.split("-", str(sdate + timedelta(days=i)))

                year = int(currentdate[0])
                month = int(currentdate[1])
                day = int(currentdate[2])

                dates_to_create.append((year, month, day))
        else:
            dates_to_create.append((year, month, day))

        for date_tuple in dates_to_create:
            year, month, day = date_tuple
            calendar_data.create_task(
                calendar_id=get_calendar_name_by_id(calendar_id),
                year=year,
                month=month,
                day=day,
                title=title,
                is_all_day=is_all_day,
                start_time=start_time,
                end_time=end_time,
                details=details,
                color=color,
                has_repetition=has_repetition,
                repetition_type=repetition_type,
                repetition_subtype=repetition_subtype,
                repetition_value=repetition_value,
            )
        return redirect('/teacher_calendar/' + calendar_id)
