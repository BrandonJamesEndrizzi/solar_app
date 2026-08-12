"""Fine-tune a T5 model on the hand-labelled solar event summaries.

This was an experiment in replacing the GPT-4 call in the main app with a local
model. It is not wired into the report pipeline.
"""

from pathlib import Path

import custom_tokenizer_script
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, TensorDataset
from transformers import T5ForConditionalGeneration, T5Tokenizer

TOKENIZER_DIR = Path(__file__).resolve().parent
TRAIN_DATA_PATH = TOKENIZER_DIR / "train_data.json"
MODEL_OUTPUT_DIR = TOKENIZER_DIR.parent / "model"

# t5-small trains on a laptop; t5-3b needs a serious GPU.
BASE_MODEL = "t5-small"
BATCH_SIZE = 12
NUM_EPOCHS = 3
LEARNING_RATE = 5e-5


def pad(sequences, pad_token_id, max_length):
    return [
        sequence + [pad_token_id] * (max_length - len(sequence))
        for sequence in sequences
    ]


def main():
    model = T5ForConditionalGeneration.from_pretrained(BASE_MODEL)
    tokenizer = T5Tokenizer.from_pretrained(BASE_MODEL)

    data = custom_tokenizer_script.load_json_data(TRAIN_DATA_PATH)
    input_tokens, output_tokens = custom_tokenizer_script.process_data(data)

    input_ids = [tokenizer.convert_tokens_to_ids(tokens) for tokens in input_tokens]
    output_ids = [tokenizer.convert_tokens_to_ids(tokens) for tokens in output_tokens]

    max_length = max(
        max(len(sequence) for sequence in input_ids),
        max(len(sequence) for sequence in output_ids),
    )
    input_ids = pad(input_ids, tokenizer.pad_token_id, max_length)
    output_ids = pad(output_ids, tokenizer.pad_token_id, max_length)

    dataset = TensorDataset(torch.tensor(input_ids), torch.tensor(output_ids))
    loader = DataLoader(dataset, batch_size=BATCH_SIZE)
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

    model.train()
    for epoch in range(NUM_EPOCHS):
        for input_batch, output_batch in loader:
            optimizer.zero_grad()
            outputs = model(input_ids=input_batch, labels=output_batch)
            outputs.loss.backward()
            optimizer.step()
            print(f"Epoch: {epoch}, Loss: {outputs.loss.item()}")

    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(MODEL_OUTPUT_DIR)
    print(f"Model saved to {MODEL_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
