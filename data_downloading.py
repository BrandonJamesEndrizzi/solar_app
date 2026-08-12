"""Download the JSON feeds and solar images named in config.ini."""

import json
import time

import requests

from settings import data_path, load_config

REQUEST_TIMEOUT = 30


def _lookup(question):
    """Return (url, destination_path) for a config key prefix such as 'solar_events'."""
    config = load_config()
    url = config.get("URLs", f"{question}_url")
    filename = config.get("Paths", f"{question}_file")
    return url, data_path(filename)


def download_json(question):
    """Fetch a JSON feed, cache it to data_dump/, and return the parsed data."""
    url, file_path = _lookup(question)

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as err:
        print(f"Failed to download {question} from {url}: {err}")
        return None

    try:
        data = response.json()
    except ValueError as err:
        # Outages sometimes serve an HTML error page with a 200 status.
        print(f"Invalid JSON for {question} from {url}: {err}")
        return None

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file)
    return data


def download_image(question):
    """Fetch an image, cache it to data_dump/, and return its path."""
    url, file_path = _lookup(question)

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as err:
        print(f"Failed to download {question} from {url}: {err}")
        return None

    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


def download_json_weather(base_url, headers, limit=25, pause=0.25):
    """Page through the NCEI station list and return every result.

    NCEI's Climate Data Online API allows five requests per second, so this
    pauses briefly between pages.
    """
    all_stations = []
    offset = 1
    total_stations = None

    while total_stations is None or offset < total_stations:
        paginated_url = f"{base_url}?limit={limit}&offset={offset}"

        try:
            response = requests.get(
                paginated_url, headers=headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as err:
            print(f"Failed to fetch stations at offset {offset}: {err}")
            break

        # The API returns an empty object (no "results" key) past the end.
        results = data.get("results")
        if not results:
            break
        all_stations.extend(results)

        if total_stations is None:
            total_stations = (
                data.get("metadata", {}).get("resultset", {}).get("count")
            )
            if total_stations is None:
                print("No result count in the response; stopping after one page.")
                break

        offset += limit
        time.sleep(pause)

    return all_stations
