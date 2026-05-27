# Documentation - LinkedIn Job Extension CV Matcher

This document provides comprehensive documentation for the LinkedIn Job Extension application.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)
6. [Development Guide](#development-guide)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The LinkedIn Job Extension is a Chrome extension combined with a FastAPI backend that helps job seekers analyze and match their CV against job postings using AI-powered analysis.

### Key Capabilities

- **CV-Job Matching**: Calculates compatibility percentage between your skills and job requirements
- **Skill Gap Analysis**: Identifies missing or weak skills needed for the position
- **Technology Stack Extraction**: Extracts required technologies with importance levels
- **Multi-language Support**: Automatically translates Hebrew job descriptions to English

---

## Architecture

### System Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Chrome         │────▶│  FastAPI Server  │◀────│  LM Studio      │
│  Extension      │     │  (Port 8000)     │     │  (Port 1234)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Transformers   │
                    │  Translation     │
                    │ (Port N/A - local)│
                    └──────────────────┘
```

### Data Flow

1. User submits job data via Chrome extension
2. Backend receives JSON with URL, title, and description
3. Language detection runs on the description
4. If non-English detected, translation occurs before processing
5. CV text is extracted from PDF file
6. AI analysis generates match score and skill analysis
7. Results are returned to frontend for display

---

## Components

### Backend (`main.py`)

The main FastAPI application that orchestrates all processing:

```python
@app.post("/job")
async def receive_job(job: JobData):
    # 1. Detect language
    lang = check_language(description)
    
    # 2. Translate if needed
    if lang != "english":
        description = translate_to_english(description)
        title = translate_to_english(title)
    
    # 3. Extract CV text
    cv_text = get_cv_text()
    
    # 4. Run AI analysis
    analysis = ask_ollama(cv_text=cv_text, job_title=title, job_description=description)
```

### Job Data Model (`ollama.py`)

Pydantic model for structured job data:

```python
class JobData(BaseModel):
    url: str      # LinkedIn job URL
    title: str    # Job title
    description: str  # Full job description
```

### AI Analysis Functions

#### `ask_ollama()` - CV Matching Analysis

Analyzes compatibility between CV and job requirements.

**Prompt Template:**
- Uses strict rules to avoid hallucination
- Returns JSON with match percentage, matching skills, missing skills, and reasoning
- Token limit: 1000 tokens maximum

**Output Schema:**
```json
{
    "match_percent": number,           // 0-100 compatibility score
    "matching_job_skills": string[],   // List of matched skills
    "missing_skills": [                // Array of missing/weak skills
        {
            "skill": string,
            "what_is_it": string        // Explanation of the skill
        }
    ],
    "score_reason": string             // Human-readable explanation
}
```

#### `ask_ollama_technologies()` - Technology Extraction

Extracts required technologies from job descriptions.

**Output Schema:**
```json
{
    "technologies": [
        {
            "name": string,            // Technology name
            "level": "strong" | "intermediate" | "basic",
            "explanation": string      // 2-sentence explanation
        }
    ],
    "job_title": string                // Original job title for context
}
```

### Translation Module (`translator.py`)

Hebrew to English translation using MarianMT model.

**Features:**
- Regex-based language detection (Hebrew Unicode range: `\u0590-\u05FF`)
- Chunked processing for long texts (>512 tokens)
- 60-second timeout per chunk
- CPU-only operation to avoid GPU conflicts

### CV Processing (`get_cv.py`)

PDF text extraction and cleaning.

**Features:**
- Uses PyMuPDF (fitz) for PDF parsing
- Smart line merging based on content patterns
- Preserves section headers as separate lines
- Removes excessive whitespace

---

## API Reference

### Base URL
```
http://127.0.0.1:8000
```

### Endpoints Summary

| Method | Endpoint      | Description                    |
|--------|---------------|--------------------------------|
| GET    | `/`           | Health check                   |
| POST   | `/job`        | Analyze job vs CV match        |
| POST   | `/technologies` | Extract technologies from job  |

### Request/Response Examples

See [README.md](../README.md) for detailed API documentation with examples.

---

## Configuration

### Environment Variables (Optional)

```python
# ollama.py constants
CV_FILE_PATH = Path("CV.pdf")           # Path to CV PDF file
LM_STUDIO_URL   = "http://127.0.0.1:1234/v1/chat/completions"
LM_STUDIO_MODEL = "unsloth/qwen3.5-9b"

# translator.py constants
MODEL_NAME = "Helsinki-NLP/opus-mt-tc-big-he-en"
MAX_TRANSLATION_TIME = 60               # seconds per chunk
MAX_INPUT_LENGTH = 512                  # tokens per chunk
```

### Dependencies (`requirements.txt`)

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
requests==2.31.0
transformers==4.40.0
torch==2.2.1
pymupdf==1.23.9
```

---

## Development Guide

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-job-extension
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your CV**
   - Place `CV.pdf` in the project root directory
   - Ensure PDF is text-based (not scanned images)

4. **Start LM Studio**
   - Download from https://lmstudio.ai/
   - Load model: `unsloth/qwen3.5-9b`
   - Start local server on port 1234

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Load Chrome Extension**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `linkedin-job-extension/` folder

### Adding New Features

1. Create a new module in the appropriate location
2. Define input/output schemas using Pydantic models
3. Add type hints to all functions
4. Write unit tests for new functionality
5. Update API documentation if endpoints change

### Testing Guidelines

- Test with various PDF formats and layouts
- Verify translation accuracy with different Hebrew texts
- Check token usage limits are respected
- Validate JSON output format consistency

---

## Troubleshooting

### Common Issues

#### "CV.pdf not found" Error
**Solution:** Ensure `CV.pdf` exists in the project root directory.

#### Translation Timeout
**Symptom:** Application hangs during translation
**Cause:** Job description exceeds 512 tokens and takes >60 seconds per chunk
**Solution:** Reduce job description length or increase timeout in `translator.py`

#### LM Studio Connection Failed
**Error Message:** `LM Studio request failed: Connection refused`
**Solutions:**
1. Verify LM Studio is running
2. Check port 1234 is not blocked by firewall
3. Confirm correct model is loaded in LM Studio

#### JSON Parse Error from Ollama
**Symptom:** Raw response printed instead of parsed JSON
**Cause:** Model returns markdown code fences or unexpected format
**Solution:** The regex cleaning in `ollama.py` should handle this, but you can increase timeout or adjust temperature parameter.

### Debug Mode

Enable verbose logging by modifying `ollama.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Performance Considerations

- **Translation**: ~30-60 seconds for long job descriptions (chunked processing)
- **AI Analysis**: ~5-15 seconds depending on model and description length
- **Token Usage**: Typically 2000-4000 tokens per complete analysis cycle

### Optimization Tips

1. Use smaller models for faster responses (if accuracy permits)
2. Cache CV text extraction with `@lru_cache` decorator
3. Consider async processing for long-running operations
4. Implement request queuing to handle multiple simultaneous requests

---

## Security Notes

- **PDF Upload**: Currently uses local file (`CV.pdf`). For production, implement secure upload mechanism.
- **API Keys**: No API keys are used; LM Studio runs locally.
- **CORS**: Enabled for all origins in development. Restrict in production.

---

## License

MIT License - See LICENSE file for details.
