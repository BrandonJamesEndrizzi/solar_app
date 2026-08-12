"""Fetch recent New York Times articles and build a summarization prompt."""

import requests

from settings import require_env

SEARCH_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
REQUEST_TIMEOUT = 30


def get_news(query="election", page=0):
    """Return a list of article documents, or an empty list on failure."""
    params = {
        "q": query,
        "sort": "newest",
        "page": page,
        "api-key": require_env("NYT_API_KEY"),
    }

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as err:
        print(f"Failed to fetch news: {err}")
        return []

    return response.json()["response"]["docs"]


def build_prompt(query="election"):
    """Return a summarization prompt built from recent articles, or '' if none."""
    articles = get_news(query)
    if not articles:
        return ""

    summaries = [
        {
            "headline": article["headline"]["main"],
            "subject": article.get("section_name", ""),
            "body": article.get("abstract", ""),
        }
        for article in articles
    ]

    return (
        "Analyze the following articles and give a one paragraph summary of the "
        f"information. Here are the articles: {summaries}"
    )


if __name__ == "__main__":
    print(build_prompt())
