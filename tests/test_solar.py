import pytest

pytest.importorskip("cv2")
pytest.importorskip("requests")
pytest.importorskip("dotenv")

import solar


def test_build_prompt_includes_data_and_count():
    prompt = solar.build_prompt("EVENTS_TEXT", "ALERTS_TEXT", 5)
    assert "Number of sunspots: 5" in prompt
    assert "EVENTS_TEXT" in prompt
    assert "ALERTS_TEXT" in prompt
