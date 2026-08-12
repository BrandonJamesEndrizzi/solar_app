"""Date helpers for the New York Times API."""


def date_dash_formatting(date):
    """Convert YYYY-MM-DD to the YYYYMMDD format the NYT API expects."""
    return date.replace("-", "")
