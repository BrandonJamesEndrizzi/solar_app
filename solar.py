"""Assemble the solar half of the report: download, filter, format, analyze."""

from pathlib import Path
from typing import NamedTuple

import data_downloading
import data_filtered
import data_formatting
import data_saving
from analyze_image import process_sun_image
from settings import data_path

# The first key is the 193 Å image the sunspot detector is tuned for.
IMAGE_KEYS = ("solar_image", "solar_image_red", "solar_image_yellow")


class SolarReport(NamedTuple):
    """Everything the email layer needs from the solar pipeline."""

    prompt: str
    attachments: list[Path]
    inline_image_path: Path | None
    sunspot_count: int


def build_prompt(formatted_events, formatted_alerts, sunspot_count):
    return (
        "Analyze the following solar event and space weather alert data. Provide a "
        "summary that includes:\n"
        "- Potential impacts on Earth's technology and environment.\n"
        "- Historical comparisons to similar past events.\n"
        "- Predictive analysis for future events.\n"
        "Use wording that is easy for hobbyists to understand. Explain any impactful "
        "events or alerts, and detail the classes and severity of solar flares or "
        "events. Also include the number of sunspots in your response.\n"
        f"Number of sunspots: {sunspot_count}\n"
        f"Event Data: {formatted_events}\n"
        f"Alert Data: {formatted_alerts}"
    )


def build_report(start_date, end_date):
    """Download and analyze solar data for a date range, and return a SolarReport."""
    solar_events = data_downloading.download_json("solar_events") or []
    solar_alerts = data_downloading.download_json("solar_alerts") or []

    image_paths = {}
    for key in IMAGE_KEYS:
        path = data_downloading.download_image(key)
        if path is not None:
            image_paths[key] = path

    filtered_events = data_filtered.filter_events_by_date(
        solar_events, start_date, end_date
    )
    filtered_alerts = data_filtered.filter_alerts_by_date(
        solar_alerts, start_date, end_date
    )

    formatted_events = data_formatting.format_events_data(filtered_events)
    formatted_alerts = data_formatting.format_alerts_data(filtered_alerts)

    # Only the 193 Å image is suitable for sunspot detection; if it failed to
    # download, skip the analysis rather than running it on another wavelength.
    sunspot_count = 0
    annotated_image = None
    primary_image = image_paths.get(IMAGE_KEYS[0])
    if primary_image is not None:
        sunspot_count, annotated_image = process_sun_image(primary_image)

    attachments = []
    events_file = data_path("solar_events_data.txt")
    data_saving.save_data_to_file(events_file, formatted_events)
    attachments.append(events_file)

    alerts_file = data_path("solar_alerts_data.txt")
    data_saving.save_data_to_file(alerts_file, formatted_alerts)
    attachments.append(alerts_file)

    attachments.extend(image_paths.values())

    return SolarReport(
        prompt=build_prompt(formatted_events, formatted_alerts, sunspot_count),
        attachments=attachments,
        inline_image_path=annotated_image,
        sunspot_count=sunspot_count,
    )


if __name__ == "__main__":
    import datetime

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    report = build_report(
        yesterday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    )
    print(f"Sunspots detected: {report.sunspot_count}")
    print(f"Attachments: {report.attachments}")
