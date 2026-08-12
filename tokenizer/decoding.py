"""Decode a list of T5 token IDs back to text, for inspecting tokenizer output."""

from transformers import T5Tokenizer

BASE_MODEL = "t5-small"

SAMPLE_TOKEN_IDS = [
    7638, 30404, 6, 29835, 2, 858, 2, 144, 2596, 10, 3449, 10, 1206, 12137,
    9491, 152, 4, 18, 25619, 2, 599, 2, 61, 2, 5, 634, 2, 19054, 2555, 2, 232,
    632, 2, 232, 9491, 2, 7152, 532, 2, 2, 634, 4, 18, 25619, 2, 8399, 9, 30989,
]


def decode(token_ids, base_model=BASE_MODEL):
    tokenizer = T5Tokenizer.from_pretrained(base_model)
    return tokenizer.decode(token_ids)


if __name__ == "__main__":
    print(decode(SAMPLE_TOKEN_IDS))
