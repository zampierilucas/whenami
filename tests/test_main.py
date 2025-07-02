import pytest
from zoneinfo import available_timezones
from whenami.main import list_timezones

def test_list_timezones(capsys):
    """Test that list_timezones prints all available timezones"""
    with pytest.raises(SystemExit) as e:
        list_timezones()

    assert e.value.code == 0

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split('\n')
    expected_timezones = sorted(available_timezones())

    assert len(output_lines) == len(expected_timezones)
    assert output_lines == expected_timezones
