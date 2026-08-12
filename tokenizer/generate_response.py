"""Load a fine-tuned T5 model and generate text from it."""

from transformers import T5ForConditionalGeneration, T5Tokenizer


def load_model(model_path):
    return T5ForConditionalGeneration.from_pretrained(model_path)


def load_tokenizer(tokenizer_path):
    """Load the tokenizer saved next to the model by custom_training.py."""
    return T5Tokenizer.from_pretrained(tokenizer_path)


def generate_text(input_text, model, tokenizer):
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(input_ids)
    return tokenizer.decode(output[0], skip_special_tokens=True)
