"""Filter the raw NOAA feeds down to a date range."""

from datetime import datetime, timedelta

# If a range contains no alerts, step back a day at a time up to this many times.
MAX_LOOKBACK_DAYS = 10


def _parse_datetime(value):
    """Return a datetime for an ISO string, or None if it is missing or malformed.

    The NOAA feeds occasionally contain records with null or absent timestamps;
    those records are skipped rather than crashing the run.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def filter_events_by_date(events, start_date, end_date):
    """Return events whose begin_datetime falls within the range."""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    matches = []
    for event in events:
        begin = _parse_datetime(event.get("begin_datetime"))
        if begin is not None and start <= begin <= end:
            matches.append(event)
    return matches


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
        matches = []
        for alert in alerts:
            issued = _parse_datetime(alert.get("issue_datetime"))
            if issued is not None and start <= issued <= end:
                matches.append(alert)
        if matches:
            return matches

        print("No alerts found for the specified date range; checking the day before.")
        start -= timedelta(days=1)
        end -= timedelta(days=1)

    return []
