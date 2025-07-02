from datetime import datetime, timedelta
from whenami.utils.calendar import format_duration, is_workday


def test_format_duration():
    td = timedelta(hours=2, minutes=30)
    assert format_duration(td) == "2 hours 30 minutes"


def test_is_workday():
    # Monday
    monday = datetime(2024, 1, 1)
    assert is_workday(monday) is True

    # Sunday
    sunday = datetime(2024, 1, 7)
    assert is_workday(sunday) is False
