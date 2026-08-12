# Tokenizer experiments

An attempt at replacing the GPT-4 call in the main app with a locally fine-tuned
T5 model, so the daily report wouldn't depend on a paid API.

These scripts are **not wired into the report pipeline** — `main.py` never imports
them. They're kept here because the custom tokenizer is the interesting part: NOAA
event records are structured key-value data, not prose, so `custom_tokenizer_script.py`
flattens each field into `key : value` token runs rather than treating the record
as a sentence.

| File | Purpose |
|---|---|
| `custom_tokenizer_script.py` | Flattens NOAA event dicts into token lists |
| `custom_training.py` | Fine-tunes T5 on `train_data.json` |
| `generate_response.py` | Loads a trained model and generates text |
| `test_response.py` | Smoke test against one sample event |
| `decoding.py` | Decodes token IDs back to text for inspection |
| `train_data.json` | Hand-written event/summary pairs |

## Running

```bash
pip install -r tokenizer/requirements.txt
python tokenizer/custom_training.py   # writes ../model/
python tokenizer/test_response.py
```

The training set is small (a handful of hand-labelled examples), so the output is
not competitive with the GPT-4 path. `BASE_MODEL` in `custom_training.py` defaults
to `t5-small` so it runs on a laptop.
