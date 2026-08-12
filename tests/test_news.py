import pytest

pytest.importorskip("requests")
pytest.importorskip("dotenv")

import news


def test_build_prompt_returns_empty_when_no_articles(monkeypatch):
    monkeypatch.setattr(news, "get_news", lambda query="election": [])
    assert news.build_prompt() == ""


def test_build_prompt_includes_article_fields(monkeypatch):
    articles = [
        {
            "headline": {"main": "Sun erupts"},
            "section_name": "Science",
            "abstract": "A large flare was observed.",
        }
    ]
    monkeypatch.setattr(news, "get_news", lambda query="election": articles)

    prompt = news.build_prompt()
    assert "Sun erupts" in prompt
    assert "A large flare was observed." in prompt


def test_build_prompt_tolerates_missing_headline(monkeypatch):
    articles = [{"abstract": "No headline on this one."}]
    monkeypatch.setattr(news, "get_news", lambda query="election": articles)

    prompt = news.build_prompt()
    assert "No headline on this one." in prompt
