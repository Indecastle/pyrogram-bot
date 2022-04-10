import calendar
from datetime import datetime
from typing import Union


def get_unix_date(utc_time: Union[datetime, datetime.date] = None) -> int:
    if utc_time is None:
        utc_time = datetime.today().date()
    return calendar.timegm(utc_time.timetuple())
