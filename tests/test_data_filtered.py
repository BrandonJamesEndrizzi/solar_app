import data_filtered


def test_events_inside_range_are_kept():
    events = [
        {"begin_datetime": "2024-01-10T05:00:00", "type": "in"},
        {"begin_datetime": "2024-01-05T00:00:00", "type": "before"},
        {"begin_datetime": "2024-02-01T00:00:00", "type": "after"},
    ]
    result = data_filtered.filter_events_by_date(events, "2024-01-09", "2024-01-11")
    assert [event["type"] for event in result] == ["in"]


def test_events_range_boundaries_are_inclusive():
    events = [
        {"begin_datetime": "2024-01-09T00:00:00"},
        {"begin_datetime": "2024-01-11T00:00:00"},
    ]
    result = data_filtered.filter_events_by_date(events, "2024-01-09", "2024-01-11")
    assert len(result) == 2


def test_events_with_missing_or_bad_datetimes_are_skipped():
    events = [
        {"begin_datetime": None},
        {},
        {"begin_datetime": "not a date"},
        {"begin_datetime": "2024-01-10T05:00:00"},
    ]
    result = data_filtered.filter_events_by_date(events, "2024-01-09", "2024-01-11")
    assert len(result) == 1


def test_alerts_in_range_are_returned_directly():
    alerts = [{"issue_datetime": "2024-01-10 05:00:00.000"}]
    result = data_filtered.filter_alerts_by_date(alerts, "2024-01-09", "2024-01-11")
    assert result == alerts


def test_alerts_lookback_widens_to_older_alerts():
    alerts = [{"issue_datetime": "2024-01-02 12:00:00.000"}]
    result = data_filtered.filter_alerts_by_date(alerts, "2024-01-08", "2024-01-09")
    assert result == alerts


def test_alerts_beyond_lookback_return_empty():
    alerts = [{"issue_datetime": "2023-11-01 12:00:00.000"}]
    result = data_filtered.filter_alerts_by_date(alerts, "2024-01-08", "2024-01-09")
    assert result == []


def test_no_alerts_returns_empty():
    assert data_filtered.filter_alerts_by_date([], "2024-01-08", "2024-01-09") == []


def test_alerts_with_bad_datetimes_do_not_crash():
    alerts = [{"issue_datetime": "garbage"}, {}]
    result = data_filtered.filter_alerts_by_date(alerts, "2024-01-08", "2024-01-09")
    assert result == []
