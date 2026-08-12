"""Date-ranged New York Times search, used for backfilling older articles.

Unlike news.py, this walks the date range backwards until it finds results, which
is useful when a narrow window returns nothing.
"""

import datetime

import requests

from date_formatting import date_dash_formatting as dash_f
from settings import require_env

SEARCH_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
REQUEST_TIMEOUT = 30
MAX_ATTEMPTS = 5


def get_news(begin_date_formatted, end_date_formatted):
    """Return articles in a date range, or an empty list on failure."""
    params = {
        "q": "election",
        "sort": "newest",
        "fq": 'body:("Science", "Politics", "Financial")',
        "begin_date": begin_date_formatted,
        "end_date": end_date_formatted,
        "page": 0,
        "api-key": require_env("NYT_API_KEY"),
    }

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as err:
        print(f"Failed to fetch news: {err}")
        return []

    return data.get("response", {}).get("docs", [])


def main(begin_date, end_date):
    """Print articles in the range, stepping the window back a week at a time."""
    begin_date_formatted = dash_f(begin_date)
    end_date_formatted = dash_f(end_date)

    for _ in range(MAX_ATTEMPTS):
        articles = get_news(begin_date_formatted, end_date_formatted)

        if articles:
            for article in articles:
                print(f"Headline: {article['headline']['main']}")
                print(f"Date: {article['pub_date']}")
                print(f"Snippet: {article['snippet']}")
                print("---------------")
            return articles

        print(f"No articles found between {begin_date} and {end_date}.")
        end_date = (
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
            - datetime.timedelta(days=7)
        ).strftime("%Y-%m-%d")
        end_date_formatted = dash_f(end_date)

    print("Max attempts reached. No articles found.")
    return []


if __name__ == "__main__":
    today = datetime.date.today()
    main(
        (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d"),
    )
