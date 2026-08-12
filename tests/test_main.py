import configparser
import datetime

import pytest

# main pulls in the whole pipeline, so these tests need the real dependencies.
pytest.importorskip("cv2")
pytest.importorskip("openai")
pytest.importorskip("requests")
pytest.importorskip("dotenv")

import main


def make_config(text):
    parser = configparser.ConfigParser()
    parser.read_string(text)
    return parser


def expected_range(days_back):
    """Build the expected (start, end) tuple for a report window."""
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days_back)
    return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")


def test_daily_range_covers_one_day():
    before = expected_range(1)
    result = main.get_date_range(main.DAILY)
    after = expected_range(1)
    # Tolerate a midnight rollover between building the expectation and the call.
    assert result in (before, after)


def test_weekly_range_covers_seven_days():
    before = expected_range(7)
    result = main.get_date_range(3)
    after = expected_range(7)
    assert result in (before, after)


@pytest.mark.parametrize("frequency", [-1, 7, 100])
def test_invalid_frequency_raises(frequency):
    with pytest.raises(ValueError):
        main.get_date_range(frequency)


def test_daily_reports_are_always_due():
    assert all(main.is_due_today(main.DAILY, day) for day in range(7))


def test_weekly_reports_are_due_on_their_day_only():
    assert main.is_due_today(2, 2)
    assert not main.is_due_today(2, 3)
    assert main.is_due_today(0, 0)


def test_read_recipient_returns_frequency_and_themes():
    config = make_config(
        "[you@example.com]\nfrequency = 2\nthemes = solar , news\n"
    )
    assert main.read_recipient(config, "you@example.com") == (2, ["solar", "news"])


def test_read_recipient_missing_section_is_skipped():
    config = make_config("[Email]\nrecipients = you@example.com\n")
    assert main.read_recipient(config, "you@example.com") is None


def test_read_recipient_missing_option_is_skipped():
    # Regression test: a section without "themes" used to crash the whole run.
    config = make_config("[you@example.com]\nfrequency = 1\n")
    assert main.read_recipient(config, "you@example.com") is None


def test_read_recipient_non_numeric_frequency_is_skipped():
    config = make_config(
        "[you@example.com]\nfrequency = daily\nthemes = solar\n"
    )
    assert main.read_recipient(config, "you@example.com") is None


def test_read_recipient_empty_themes_is_skipped():
    config = make_config("[you@example.com]\nfrequency = 1\nthemes = ,\n")
    assert main.read_recipient(config, "you@example.com") is None
