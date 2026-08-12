import date_formatting


def test_dashes_removed():
    assert date_formatting.date_dash_formatting("2024-01-10") == "20240110"


def test_no_dashes_is_unchanged():
    assert date_formatting.date_dash_formatting("20240110") == "20240110"
