import email_formatting


def test_solar_only_report_omits_image_and_news():
    body = email_formatting.get_html_email_body(
        "disclaimer", "image intro", None, "solar text", ""
    )
    assert "disclaimer" in body
    assert "solar text" in body
    assert "<img" not in body
    assert "recent news" not in body


def test_inline_image_uses_the_cid():
    body = email_formatting.get_html_email_body(
        "disclaimer", "image intro", "solar_image", "solar text", ""
    )
    assert '<img src="cid:solar_image"' in body
    assert "image intro" in body


def test_news_section_is_included_when_present():
    body = email_formatting.get_html_email_body(
        "disclaimer", "image intro", None, "", "news text"
    )
    assert "news text" in body
    assert "recent news" in body


def test_summaries_are_html_escaped():
    body = email_formatting.get_html_email_body(
        "a & b", "intro", None, "<script>alert(1)</script>", ""
    )
    assert "<script>" not in body
    assert "&lt;script&gt;" in body
    assert "a &amp; b" in body
