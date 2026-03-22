import time
import logging
from pathlib import Path
from pydantic import BaseModel
import json, logging, requests, re
# ------------------------------------------------------------------- constants
CV_FILE_PATH = Path("CV.pdf")

# ------------------------------------------------------------------- models
class JobData(BaseModel):
    url: str
    title: str
    description: str


OLLAMA_URL   = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"

def ask_ollama(cv_text: str, job_title: str, job_description: str) -> str:
    prompt = f"""
You are a strict CV‑job matching assistant.

STRICT RULES:
- Use ONLY explicit information from the CV and job description
- Do NOT guess, infer, or assume missing skills

OUTPUT FORMAT:
Return ONLY valid JSON as plain text (no markdown, no fences).

{{"match_percent": number, "matching_job_skills": string[], "missing_skills": [{{"skill": string, "what_is_it": string}}], "score_reason": string}}

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description}
CV: {cv_text}
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "repeat_penalty": 1.1},
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"Ollama request failed: {e}")
        return json.dumps({"error": str(e)})
    
    # Ollama may return plain text or a JSON wrapper
    try:
        data = resp.json()
        raw = data.get("response", "")
    except ValueError:
        raw = resp.text

    # print the number of tokens used for this request
    prompt_tokens   = data.get("prompt_eval_count")   # tokens in the prompt
    response_tokens = data.get("eval_count")         # tokens generated
    total_tokens    = (
        prompt_tokens + response_tokens
        if isinstance(prompt_tokens, int) and isinstance(response_tokens, int)
        else None
    )
    print(
        f"Tokens → prompt: {prompt_tokens or 'n/a'} | "
        f"response: {response_tokens or 'n/a'} | "
        f"total: {total_tokens or 'n/a'}"
    )

    # Clean possible markdown fences
    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```$", "", raw).strip()
    return raw

