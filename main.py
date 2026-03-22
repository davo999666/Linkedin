import json
import time
from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from get_cv import read_pdf_text
from ollama import JobData, ask_ollama, CV_FILE_PATH
from translator import check_language, translate_to_english

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_cv_text() -> str:
    return read_pdf_text(CV_FILE_PATH)


@app.get("/")
async def root() -> dict:
    return {"message": "FastAPI server is working"}


@app.post("/job")
async def receive_job(job: JobData):
    start = time.perf_counter()

    try:
        title = job.title
        description = job.description

        lang = check_language(description)
        if lang != "english":
            print("Detected non-English job description. Translating to English...")
            description = translate_to_english(description)
            title = translate_to_english(title)

        cv_text = get_cv_text()


        analysis_str = ask_ollama(
            cv_text=cv_text,
            job_title=title,
            job_description=description,
        )

        try:
            analysis = json.loads(analysis_str)
        except json.JSONDecodeError:
            print("Failed to parse JSON from Ollama:")
            print(analysis_str)
            analysis = {"raw_response": analysis_str}

        duration = time.perf_counter() - start

        return {
            "status": "ok",
            "job_url": job.url,
            "job_title": title,
            "analysis": analysis,
            "processing_time_sec": round(duration, 2),
        }

    except Exception as e:
        print("ERROR:", str(e))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
            },
        )