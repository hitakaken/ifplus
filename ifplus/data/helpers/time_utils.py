import datetime
import time
import calendar


def utcnow():
    return datetime.datetime.utcnow()


def timestamp(convert_time):
    if convert_time is None:
        return None
    return int(calendar.timegm(convert_time.timetuple()) * 1000 + convert_time.microsecond / 1000)
