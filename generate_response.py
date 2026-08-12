"""GPT-4 summaries of the solar and news data."""

from openai import OpenAI

from settings import require_env

MODEL = "gpt-4-turbo-preview"

SOLAR_SYSTEM_PROMPT = (
    "You are an assistant that analyzes and summarizes solar event and alert data. "
    "Generate a concise, accurate, and easily understandable summary suitable for a "
    "general audience. Respond in plain text only, without markdown or other special "
    "formatting, as a single paragraph with no headings or separators. Include an "
    "explanation of any solar flare classes present in the data: A and B classes are "
    "the smallest with no impact on Earth, C are minor, M are medium, and X are "
    "dangerous."
)

NEWS_SYSTEM_PROMPT = (
    "You are an assistant that analyzes lengthy news articles and condenses them into "
    "a single easily readable paragraph."
)


def _client():
    return OpenAI(api_key=require_env("OPENAI_API_KEY"))


def _summarize(system_prompt, prompt, max_tokens):
    response = _client().chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def generate_response_solar(prompt):
    """Summarize solar event and alert data."""
    return _summarize(SOLAR_SYSTEM_PROMPT, prompt, max_tokens=205)


def generate_response_news(prompt):
    """Summarize a batch of news articles."""
    return _summarize(NEWS_SYSTEM_PROMPT, prompt, max_tokens=350)
