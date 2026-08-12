import json

import pytest

pytest.importorskip("requests")
pytest.importorskip("dotenv")

import requests

import data_downloading


class FakeResponse:
    def __init__(self, payload=None, invalid_json=False, http_error=False):
        self._payload = payload
        self._invalid_json = invalid_json
        self._http_error = http_error

    def raise_for_status(self):
        if self._http_error:
            raise requests.RequestException("boom")

    def json(self):
        if self._invalid_json:
            raise ValueError("not json")
        return self._payload

    @property
    def content(self):
        return b"bytes"


def fake_lookup(tmp_path):
    return lambda question: ("https://example.test/feed", tmp_path / "feed.json")


def test_download_json_returns_and_caches_data(monkeypatch, tmp_path):
    monkeypatch.setattr(data_downloading, "_lookup", fake_lookup(tmp_path))
    monkeypatch.setattr(
        data_downloading.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(payload={"ok": True}),
    )

    assert data_downloading.download_json("solar_events") == {"ok": True}
    with open(tmp_path / "feed.json", encoding="utf-8") as file:
        assert json.load(file) == {"ok": True}


def test_download_json_handles_http_errors(monkeypatch, tmp_path):
    monkeypatch.setattr(data_downloading, "_lookup", fake_lookup(tmp_path))
    monkeypatch.setattr(
        data_downloading.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(http_error=True),
    )

    assert data_downloading.download_json("solar_events") is None


def test_download_json_handles_invalid_json(monkeypatch, tmp_path):
    # Regression test: outage pages that are not JSON used to crash the run.
    monkeypatch.setattr(data_downloading, "_lookup", fake_lookup(tmp_path))
    monkeypatch.setattr(
        data_downloading.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(invalid_json=True),
    )

    assert data_downloading.download_json("solar_events") is None
    assert not (tmp_path / "feed.json").exists()


def test_download_image_writes_bytes(monkeypatch, tmp_path):
    monkeypatch.setattr(data_downloading, "_lookup", fake_lookup(tmp_path))
    monkeypatch.setattr(
        data_downloading.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )

    path = data_downloading.download_image("solar_image")
    assert path == tmp_path / "feed.json"
    assert path.read_bytes() == b"bytes"


def test_weather_pager_collects_all_pages(monkeypatch):
    pages = [
        FakeResponse(
            payload={
                "results": [{"id": 1}, {"id": 2}],
                "metadata": {"resultset": {"count": 4}},
            }
        ),
        FakeResponse(payload={"results": [{"id": 3}, {"id": 4}]}),
    ]
    monkeypatch.setattr(
        data_downloading.requests,
        "get",
        lambda *args, **kwargs: pages.pop(0),
    )

    stations = data_downloading.download_json_weather(
        "https://example.test/stations", headers={}, limit=2, pause=0
    )
    assert [station["id"] for station in stations] == [1, 2, 3, 4]


def test_weather_pager_stops_on_empty_response(monkeypatch):
    # Regression test: an empty object past the end used to raise KeyError.
    monkeypatch.setattr(
        data_downloading.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(payload={}),
    )

    stations = data_downloading.download_json_weather(
        "https://example.test/stations", headers={}, limit=2, pause=0
    )
    assert stations == []
