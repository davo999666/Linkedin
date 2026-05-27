import time
import logging
from pathlib import Path
from pydantic import BaseModel
import json, logging, requests, re
# ------------------------------------------------------------------- constants
CV_FILE_PATH = Path("CV.pdf")
LM_STUDIO_URL   = "http://127.0.0.1:1234/v1/chat/completions"
LM_STUDIO_MODEL = "unsloth/qwen3.5-9b"
# ------------------------------------------------------------------- models
class JobData(BaseModel):
    url: str
    title: str
    description: str


def ask_ollama(cv_text: str, job_title: str, job_description: str) -> str:
    prompt = f"""
You are a strict CV‑job matching assistant.

STRICT RULES:
- Use at most 1000 tokens for the response
- Use ONLY explicit information from the CV and job description
- Do NOT guess, infer, or assume missing skills


OUTPUT FORMAT:
Return ONLY valid JSON as plain text (no markdown, no fences).

{{
    "match_percent": number, 
    "matching_job_skills": string[], 
    "missing_skills": [{{
        "skill": string, 
        "what_is_it": string -> explanation about skil
        }}], 
    "score_reason": string
    }}

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description}
CV: {cv_text}
""".strip()

    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.1,
    }

    try:
        resp = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"LM Studio request failed: {e}")
        return json.dumps({"error": str(e)})
    
    # LM Studio returns OpenAI-compatible format
    data = {}
    try:
        data = resp.json()
        raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except (ValueError, IndexError, KeyError):
        raw = resp.text

    # print the number of tokens used for this request
    usage = data.get("usage", {})
    prompt_tokens   = usage.get("prompt_tokens")
    response_tokens = usage.get("completion_tokens")
    total_tokens    = usage.get("total_tokens")
    print(
        f"Tokens → prompt: {prompt_tokens or 'n/a'} | "
        f"response: {response_tokens or 'n/a'} | "
        f"total: {total_tokens or 'n/a'}"
    )

    # Clean possible markdown fences
    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```$", "", raw).strip()
    return raw


def ask_ollama_technologies(job_title: str, job_description: str) -> str:
    """Extract technologies and frameworks required by the job with explanations."""
    prompt = f"""
You are a technical technologies extractor.

Extract ALL technologies, programming languages, frameworks, and tools mentioned in the job description.

OUTPUT FORMAT:
Return ONLY valid JSON as plain text (no markdown, no fences).

{{
    "technologies": [
        {{
            "name": "Python",
            "level": "strong" | "intermediate" | "basic",
            "explanation": "Two sentence explanation here. First sentence what it is, second why it matters for this job."
        }},
        ...
    ],
    "job_title": "{job_title}"
}}

RULES:
- Extract ONLY explicit technologies mentioned in the job
- For each technology, provide name, level (strong/intermediate/basic), and 2-sentence explanation
- Level is based on how critical it is to the job
- Keep explanations concise and relevant to this specific job
- Return at least 3-5 technologies if available

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description}
""".strip()

    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.3,
    }

    try:
        resp = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"LM Studio request failed: {e}")
        return json.dumps({"error": str(e), "technologies": []})
    
    data = {}
    try:
        data = resp.json()
        raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except (ValueError, IndexError, KeyError):
        raw = resp.text

    usage = data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens")
    response_tokens = usage.get("completion_tokens")
    print(
        f"Technologies → prompt: {prompt_tokens or 'n/a'} | "
        f"response: {response_tokens or 'n/a'}"
    )

    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```$", "", raw).strip()
    return raw
