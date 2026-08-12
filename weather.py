"""Fetch the NCEI weather station list and map station IDs to city names."""

import data_downloading
import data_saving
from data_formatting import process_data
from settings import data_path, load_config, require_env


def read_config():
    config = load_config()
    return config.get("URLs", "weather_station_list_url")


def main():
    base_url = read_config()
    headers = {"token": require_env("NOAA_CDO_TOKEN")}

    stations = data_downloading.download_json_weather(base_url, headers)
    if not stations:
        print("No station data returned.")
        return

    data_saving.json_save(data_path("weather_data.json"), stations)
    print("Station data saved to weather_data.json.")

    station_to_city = process_data(stations)
    data_saving.json_save(data_path("weather_station_list.json"), station_to_city)
    print("Station-to-city mapping saved to weather_station_list.json.")


if __name__ == "__main__":
    main()
