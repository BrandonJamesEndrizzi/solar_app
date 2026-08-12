"""Smoke test for the fine-tuned T5 model produced by custom_training.py."""

from pathlib import Path

import generate_response

TOKENIZER_DIR = Path(__file__).resolve().parent
MODEL_PATH = TOKENIZER_DIR.parent / "model"

SAMPLE_EVENT = {
    "prompt": "Write a concise description of the event.",
    "begin_datetime": "2024-01-10T12:44:18",
    "max_datetime": "2024-01-10T12:44:18",
    "end_datetime": "2024-01-10T12:44:30",
    "observatory": "SVI",
    "type": "RBR",
    "frequency": "245",
    "particulars1": "120",
    "particulars3": "4.2E+02",
    "particulars4": "100",
}


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No model at {MODEL_PATH}. Run custom_training.py first."
        )

    model = generate_response.load_model(MODEL_PATH)
    tokenizer = generate_response.load_tokenizer(MODEL_PATH)

    output_text = generate_response.generate_text(str(SAMPLE_EVENT), model, tokenizer)
    print(f"Input: {SAMPLE_EVENT}")
    print(f"Output: {output_text}")


if __name__ == "__main__":
    main()
