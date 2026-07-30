"""Shared text extraction used by both the DB layer and question generation."""

from pathlib import Path


def extract_text(file_path: Path) -> str:
    """Return the plain-text content of a file, extracting PDF pages via pymupdf."""
    file_path = Path(file_path)
    if file_path.suffix.lower() == ".pdf":
        import fitz  # pymupdf

        with fitz.open(file_path) as doc:
            return "\n".join(page.get_text() for page in doc)
    return file_path.read_text(encoding="utf-8")
