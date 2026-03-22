"""Quick test script to diagnose Ollama connectivity and response format.

Run: python test_ollama.py
Paste the full output here so I can diagnose the error.
"""

import traceback
import requests

from ollama import OLLAMA_URL, OLLAMA_MODEL, ask_ollama


def direct_test():
    print("== ask_ollama() test ==")
    try:
        resp = ask_ollama("Test CV text", "Test Job Title", "Test job description")
        print("ask_ollama returned:\n", resp)
    except Exception:
        print("ask_ollama raised an exception:")
        traceback.print_exc()

    print("\n== Direct HTTP request test ==")
    try:
        r = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": "hello", "format": "text"}, timeout=10)
        print("Status code:", r.status_code)
        print("Response headers:", r.headers)
        print("Response text (first 2000 chars):\n", r.text[:2000])
    except Exception:
        print("Direct HTTP request failed:")
        traceback.print_exc()


if __name__ == "__main__":
    direct_test()
