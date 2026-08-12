import data_formatting


def test_events_are_numbered_and_defaulted():
    events = [
        {"type": "XRA", "begin_datetime": "2024-01-10T05:00:00"},
        {"observatory": "SVI"},
    ]
    text = data_formatting.format_events_data(events)

    assert "Event number: 1" in text
    assert "Event number: 2" in text
    assert "Event Type: XRA" in text
    assert "Observatory: SVI" in text
    # Missing fields fall back to N/A rather than crashing.
    assert "Region: N/A" in text
    assert data_formatting.SEPARATOR in text


def test_no_events_gives_empty_string():
    assert data_formatting.format_events_data([]) == ""


def test_alert_messages_are_split_and_indented():
    alerts = [
        {
            "product_id": "K04A",
            "issue_datetime": "2024-01-10 05:00:00.000",
            "message": "line one\r\nline two",
        }
    ]
    text = data_formatting.format_alerts_data(alerts)

    assert "Product ID: K04A" in text
    assert "    line one" in text
    assert "    line two" in text


def test_alerts_with_missing_fields_do_not_crash():
    text = data_formatting.format_alerts_data([{}])
    assert "Product ID: N/A" in text
    assert "Issue DateTime: N/A" in text


def test_extract_city_name():
    name = "PORTLAND INTERNATIONAL AIRPORT, OR US"
    assert data_formatting.extract_city_name(name) == "PORTLAND INTERNATIONAL AIRPORT"


def test_process_data_maps_ids_to_cities():
    stations = [{"id": "GHCND:US1", "name": "SEATTLE, WA US"}]
    assert data_formatting.process_data(stations) == {"GHCND:US1": "SEATTLE"}
