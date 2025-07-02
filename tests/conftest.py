import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

@pytest.fixture
def sample_config():
    return {
        "calendars": [
            {
                "id": "test@example.com",
                "name": "Test Calendar"
            }
        ],
        "work_hours": {
            "start": "09:00",
            "end": "17:00",
            "mid_day_break": {
                "start": "12:00",
                "end": "13:00"
            }
        },
        "minimum_slot_duration": 30
    }


@pytest.fixture
def test_timezone():
    return ZoneInfo("UTC")


@pytest.fixture
def sample_datetime():
    return datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
