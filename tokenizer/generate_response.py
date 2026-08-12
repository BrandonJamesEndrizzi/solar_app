from transformers import T5ForConditionalGeneration
from transformers import PreTrainedTokenizerFast

def load_model(model_path):
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    return model

def load_tokenizer(tokenizer_path):
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
    return tokenizer

def generate_text(input_text, model, tokenizer):
    # Tokenize the input text
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Generate output
    output = model.generate(input_ids)

    # Decode and return the output text
    decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
    return decoded_output
