# LinkedIn Job Extension - CV Matcher

A FastAPI-based application that analyzes job descriptions and matches them against your CV using AI-powered analysis. The extension provides detailed skill matching, technology extraction, and compatibility scoring for job applications.

## Features

- **CV-Job Matching**: Analyzes job descriptions and compares them with your uploaded CV
- **Skill Analysis**: Identifies matching skills and highlights missing requirements
- **Technology Extraction**: Extracts required technologies, frameworks, and tools from job postings
- **Language Translation**: Automatically detects and translates non-English (Hebrew) job descriptions to English
- **Performance Tracking**: Monitors API call token usage and processing time

## Tech Stack

- **Backend**: FastAPI with Python
- **AI/ML**: Ollama/Qwen3.5-9B for CV analysis, Transformers for translation
- **PDF Processing**: PyMuPDF (fitz) for CV text extraction
- **Frontend Extension**: Chrome extension using JavaScript

## Project Structure

```
linkedin-job-extension/
├── content.js          # Chrome extension content script
├── manifest.json       # Chrome extension manifest configuration
└── modal/
    └── modal_window.js # Modal window for job analysis results
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js (for Chrome extension)
- LM Studio running locally on `http://127.0.0.1:1234`

### Backend Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place your CV in the root directory as `CV.pdf`

3. Run the FastAPI server:
   ```bash
   python main.py
   ```

The API will be available at `http://127.0.0.1:8000`

### Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `linkedin-job-extension/` folder

## API Endpoints

### `/` - Health Check
Returns a simple health check message.

```bash
GET /
Response: {"message": "FastAPI server is working"}
```

### `/job` - Job Analysis
Analyzes a job posting and matches it against your CV.

```bash
POST /job
Content-Type: application/json

{
    "url": "https://linkedin.com/jobs/example",
    "title": "Senior Python Developer",
    "description": "Job description text here..."
}
```

**Response:**
```json
{
    "status": "ok",
    "job_url": "https://linkedin.com/jobs/example",
    "job_title": "Senior Python Developer",
    "analysis": {
        "match_percent": 75,
        "matching_job_skills": ["Python", "Django", "PostgreSQL"],
        "missing_skills": [
            {
                "skill": "AWS",
                "what_is_it": "Cloud computing platform"
            }
        ],
        "score_reason": "Strong match on core skills, missing cloud experience"
    },
    "processing_time_sec": 2.5
}
```

### `/technologies` - Technology Extraction
Extracts required technologies and frameworks from a job posting.

```bash
POST /technologies
Content-Type: application/json

{
    "url": "https://linkedin.com/jobs/example",
    "title": "Senior Python Developer",
    "description": "Job description text here..."
}
```

**Response:**
```json
{
    "status": "ok",
    "job_url": "https://linkedin.com/jobs/example",
    "job_title": "Senior Python Developer",
    "technologies": [
        {
            "name": "Python",
            "level": "strong",
            "explanation": "Primary programming language for backend development. Critical for this role as it's the main technology stack."
        },
        {
            "name": "Django",
            "level": "intermediate",
            "explanation": "Python web framework mentioned in requirements. Important for building and maintaining web applications."
        }
    ],
    "processing_time_sec": 1.8
}
```

## Language Support

The application automatically detects Hebrew text in job descriptions using regex pattern matching and translates it to English using the Helsinki-NLP translation model before processing.

## Configuration

### LM Studio Settings
- **URL**: `http://127.0.0.1:1234/v1/chat/completions`
- **Model**: `unsloth/qwen3.5-9b`

### Translation Model
- **Model Name**: `Helsinki-NLP/opus-mt-tc-big-he-en`
- **Max Input Length**: 512 tokens
- **Max Translation Time**: 60 seconds per chunk

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bug reports and feature suggestions.
