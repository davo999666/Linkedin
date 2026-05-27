import re
import time
from transformers import MarianMTModel, MarianTokenizer

# Load model once (important for performance)
# Uses CPU only to avoid GPU conflicts with LM Studio
MODEL_NAME = "Helsinki-NLP/opus-mt-tc-big-he-en"

tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
model = MarianMTModel.from_pretrained(MODEL_NAME)

# Maximum translation time in seconds
MAX_TRANSLATION_TIME = 60

# Maximum input length for the model
MAX_INPUT_LENGTH = 512


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
    Maximum translation time: 60 seconds.
    """

    # Skip if already English
    if check_language(text) == "english":
        return text

    start_time = time.time()

    try:
        # For long texts, split into chunks and translate each chunk
        if len(text) > MAX_INPUT_LENGTH:
            return _translate_chunked(text, start_time)

        inputs = tokenizer(
            [text],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_INPUT_LENGTH
        )

        translated_tokens = model.generate(
            **inputs,
            max_length=MAX_INPUT_LENGTH,
            num_beams=4,
            early_stopping=True
        )

        translated_text = tokenizer.decode(
            translated_tokens[0],
            skip_special_tokens=True
        )
        return translated_text.strip()

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"Translation failed after {elapsed:.1f}s: {e}")
        return text


def _translate_chunked(text: str, start_time: float) -> str:
    """
    Translates long text by splitting into chunks.
    """
    # Split by sentences (periods, newlines)
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    
    result_parts = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check time limit
        if time.time() - start_time > MAX_TRANSLATION_TIME:
            print(f"Translation timed out after {MAX_TRANSLATION_TIME}s, returning partial result")
            if current_chunk:
                result_parts.append(current_chunk)
            return " ".join(result_parts)
        
        if len(current_chunk) + len(sentence) > MAX_INPUT_LENGTH:
            if current_chunk:
                # Translate current chunk
                inputs = tokenizer(
                    [current_chunk],
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=MAX_INPUT_LENGTH
                )
                
                translated_tokens = model.generate(
                    **inputs,
                    max_length=MAX_INPUT_LENGTH,
                    num_beams=4,
                    early_stopping=True
                )
                
                translated = tokenizer.decode(
                    translated_tokens[0],
                    skip_special_tokens=True
                )
                result_parts.append(translated.strip())
                current_chunk = sentence
            else:
                # Single sentence too long, truncate it
                current_chunk = sentence[:MAX_INPUT_LENGTH]
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Translate remaining chunk
    if current_chunk and (time.time() - start_time <= MAX_TRANSLATION_TIME):
        inputs = tokenizer(
            [current_chunk],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_INPUT_LENGTH
        )
        
        translated_tokens = model.generate(
            **inputs,
            max_length=MAX_INPUT_LENGTH,
            num_beams=4,
            early_stopping=True
        )
        
        translated = tokenizer.decode(
            translated_tokens[0],
            skip_special_tokens=True
        )
        result_parts.append(translated.strip())
    
    return " ".join(result_parts)