"""Convenience helpers for printing the unfiltered NOAA feeds."""

import data_downloading
import data_formatting


def solar_events():
    data = data_downloading.download_json("solar_events") or []
    return data_formatting.format_events_data(data)


def solar_alerts():
    data = data_downloading.download_json("solar_alerts") or []
    return data_formatting.format_alerts_data(data)


if __name__ == "__main__":
    print(solar_events())
    print(solar_alerts())
