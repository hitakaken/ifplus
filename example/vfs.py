# -*- coding: utf-8 -*-
import datetime
import time
import calendar
now = datetime.datetime.utcnow()
print time.mktime(now.timetuple())
print int(calendar.timegm(now.timetuple()) * 1000 + now.microsecond / 1000)


