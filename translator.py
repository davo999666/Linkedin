import re
from transformers import MarianMTModel, MarianTokenizer

# Load model once (important for performance)
MODEL_NAME = "Helsinki-NLP/opus-mt-tc-big-he-en"

tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
model = MarianMTModel.from_pretrained(MODEL_NAME)


def check_language(text: str) -> str:
    """
    Checks if text contains Hebrew characters.
    """
    if re.search(r'[\u0590-\u05FF]', text):
        return "hebrew"
    return "english"


def translate_to_english(text: str) -> str:
    """
    Translates Hebrew text to English using Transformers (local model).
    """

    # Skip if already English
    if check_language(text) == "english":
        return text

    try:
        inputs = tokenizer(
            [text],
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        translated_tokens = model.generate(**inputs)

        translated_text = tokenizer.decode(
            translated_tokens[0],
            skip_special_tokens=True
        )
        return translated_text.strip()

    except Exception as e:
        print(f"Translation failed: {e}")
        return text