from pathlib import Path
import fitz  # pymupdf
import re

def clean_pdf_text(text: str) -> str:
    lines = text.splitlines()
    result = []
    current_line = ""

    # these lines should never be merged with others
    SECTION_KEYWORDS = (
        "Technologies:", "Programming Languages:", "Databases",
        "Skills &", "Tools /", "Used:", "Languages:"
    )

    for line in lines:
        line = line.strip()

        if not line:
            if current_line:
                result.append(current_line.strip())
                current_line = ""
            result.append("")
            continue

        # never merge skill/section lines
        if any(line.startswith(kw) for kw in SECTION_KEYWORDS):
            if current_line:
                result.append(current_line.strip())
            result.append(line)
            current_line = ""
            continue

        if current_line:
            if (
                len(line.split()) <= 3
                or not current_line.endswith((".", ":", ";", "•", "-", "—"))
            ):
                current_line += " " + line
            else:
                result.append(current_line.strip())
                current_line = line
        else:
            current_line = line

    if current_line:
        result.append(current_line.strip())

    cleaned = "\n".join(result)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def read_pdf_text(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"{pdf_path} not found")

    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(clean_pdf_text(text))

    full_text = "\n\n".join(pages).strip()

    if not full_text:
        raise ValueError("Could not extract text from PDF")

    return full_text