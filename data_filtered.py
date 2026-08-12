"""Filter the raw NOAA feeds down to a date range."""

from datetime import datetime, timedelta

# If a range contains no alerts, step back a day at a time up to this many times.
MAX_LOOKBACK_DAYS = 10


def filter_events_by_date(events, start_date, end_date):
    """Return events whose begin_datetime falls within the range."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    return [
        event
        for event in events
        if start <= datetime.fromisoformat(event["begin_datetime"]) <= end
    ]


def filter_alerts_by_date(alerts, start_date, end_date):
    """Return alerts in the range, widening backwards if the range is empty.

    Quiet stretches are common, so rather than send an empty report this walks the
    window back a day at a time until it finds something or gives up.
    """
    if not alerts:
        return []

    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    for _ in range(MAX_LOOKBACK_DAYS):
        matches = [
            alert
            for alert in alerts
            if start <= datetime.fromisoformat(alert["issue_datetime"]) <= end
        ]
        if matches:
            return matches

        print("No alerts found for the specified date range; checking the day before.")
        start -= timedelta(days=1)
        end -= timedelta(days=1)

    return []
