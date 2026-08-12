"""Flatten NOAA solar event records into token lists for T5 training.

NOAA events are structured key-value records rather than prose, so each field is
turned into a "key : value" token run. The 'prompt' and 'summary' fields are real
text and get word-level tokenization instead.
"""

import json
import re

WORD_PATTERN = r"\w+|[^\w\s]"


def load_json_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def tokenize_text(text):
    """Split prose into word and punctuation tokens."""
    if isinstance(text, str) and text.strip():
        return re.findall(WORD_PATTERN, text)
    return []


def tokenize_field(key, value):
    """Turn one key-value pair into tokens, e.g. 'begin datetime : 2023-12-14'."""
    value_str = str(value) if value is not None else "null"
    return f"{key.replace('_', ' ')} : {value_str}".split(" ")


def custom_tokenizer(data_entry):
    """Return (input_tokens, output_tokens) for a single event record."""
    input_tokens = []
    output_tokens = []

    if not any(value is not None for value in data_entry.values()):
        return ["EMPTY_ENTRY"], output_tokens

    for key, value in data_entry.items():
        if key == "prompt":
            input_tokens.extend(tokenize_text(value))
        elif key == "summary":
            output_tokens.extend(tokenize_text(value))
        else:
            input_tokens.extend(tokenize_field(key, value))

    return input_tokens, output_tokens


def process_data(data):
    """Tokenize a whole dataset into parallel input and output token lists."""
    input_tokens_list = []
    output_tokens_list = []

    for entry in data:
        input_tokens, output_tokens = custom_tokenizer(entry)
        input_tokens_list.append(input_tokens)
        output_tokens_list.append(output_tokens)

    return input_tokens_list, output_tokens_list
