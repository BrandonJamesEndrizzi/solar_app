import sys
from pathlib import Path

# Appended (not inserted) so the root generate_response.py keeps precedence over
# tokenizer/generate_response.py; only custom_tokenizer_script resolves here.
sys.path.append(str(Path(__file__).resolve().parent.parent / "tokenizer"))

import custom_tokenizer_script


def test_tokenize_text_splits_words_and_punctuation():
    assert custom_tokenizer_script.tokenize_text("Hello, world!") == [
        "Hello", ",", "world", "!",
    ]


def test_tokenize_text_handles_empty_and_non_string():
    assert custom_tokenizer_script.tokenize_text("") == []
    assert custom_tokenizer_script.tokenize_text("   ") == []
    assert custom_tokenizer_script.tokenize_text(None) == []


def test_tokenize_field_flattens_key_and_value():
    tokens = custom_tokenizer_script.tokenize_field("begin_datetime", "2024-01-10")
    assert tokens == ["begin", "datetime", ":", "2024-01-10"]


def test_tokenize_field_null_value():
    assert custom_tokenizer_script.tokenize_field("region", None) == [
        "region", ":", "null",
    ]


def test_custom_tokenizer_routes_prompt_and_summary():
    entry = {
        "prompt": "Describe the event.",
        "type": "RBR",
        "summary": "A radio burst.",
    }
    input_tokens, output_tokens = custom_tokenizer_script.custom_tokenizer(entry)

    assert "Describe" in input_tokens
    assert ["type", ":", "RBR"] == input_tokens[-3:]
    assert output_tokens == ["A", "radio", "burst", "."]


def test_custom_tokenizer_empty_entry():
    entry = {"type": None, "summary": None}
    assert custom_tokenizer_script.custom_tokenizer(entry) == (["EMPTY_ENTRY"], [])


def test_process_data_returns_parallel_lists():
    data = [
        {"prompt": "One.", "summary": "First."},
        {"prompt": "Two.", "summary": "Second."},
    ]
    inputs, outputs = custom_tokenizer_script.process_data(data)
    assert len(inputs) == len(outputs) == 2
    assert outputs[0] == ["First", "."]
