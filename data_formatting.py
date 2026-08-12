"""Turn the raw NOAA JSON into the plain text that goes into the prompt."""

SEPARATOR = "-----------------------------------------"


def format_alerts_data(alerts):
    """Format space weather alerts as indented, readable blocks."""
    lines = []
    for alert in alerts:
        lines.append(f"Product ID: {alert.get('product_id', 'N/A')}")
        lines.append(f"Issue DateTime: {alert.get('issue_datetime', 'N/A')}")
        lines.append("Message:")
        message = alert.get("message") or ""
        lines.extend(f"    {line}" for line in message.split("\r\n"))
        lines.append("")

    return "\n".join(lines)


def format_events_data(events):
    """Format solar events as numbered, readable blocks."""
    lines = []
    for event_number, event in enumerate(events, start=1):
        lines.append(f"Event number: {event_number}")
        lines.append(f"Event Type: {event.get('type', 'N/A')}")
        lines.append(f"Start Time: {event.get('begin_datetime', 'N/A')}")
        lines.append(f"Peak Time: {event.get('max_datetime', 'N/A')}")
        lines.append(f"End Time: {event.get('end_datetime', 'N/A')}")
        lines.append(f"Observatory: {event.get('observatory', 'N/A')}")
        lines.append(f"Region: {event.get('region', 'N/A')}")
        lines.append(f"Frequency: {event.get('frequency', 'N/A')}")
        lines.append(f"Details: {event.get('particulars1', 'N/A')}")
        lines.append(SEPARATOR)

    return "\n".join(lines)


def extract_city_name(station_name):
    """Return the city portion of an NCEI station name.

    Station names look like "PORTLAND INTERNATIONAL AIRPORT, OR US", so the text
    before the first comma is the city.
    """
    return station_name.split(",")[0]


def process_data(stations):
    """Return a mapping of station ID to city name."""
    return {
        station["id"]: extract_city_name(station["name"]) for station in stations
    }
