"""
This module contains functions for generating queries based on files pulled from the database.
"""

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import anthropic
client = anthropic.Anthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"

SAMPLE_FILES_DIR = Path(__file__).parent.parent / "Sample Files"

#Temporarily hardcoded function that gets a file, once the db layer exists this should be replaced with a real lookup
def get_file() -> Path:
    return SAMPLE_FILES_DIR / "Igneous Rocks Slide 1.pdf"

#question generation object
@dataclass
class GeneratedQuestion:
    question: str
    answer: str
    sourceFile: str

#function that actually calls the api and generates a question
def generate_question(file_path: Path | None = None) -> GeneratedQuestion:

    if file_path is None:
        file_path = get_file()
    
    with open(file_path, "rb") as f:
        base64_data = base64.standard_b64encode(f.read()).decode("utf-8")
    
    response = client.messages.create(
        model = MODEL,
        max_tokens = 500,
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": base64_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Based on this document, generate ONE quiz question that tests recall "
                            "of a key concept, along with its correct answer. Respond with ONLY a "
                            "JSON object in this exact shape, no other text, no markdown fences: "
                            '{"question": "...", "answer": "..."}'
                        ),
                    },
                ],
            }
        ],
    )

    text_block = next((b for b in response.content if b.type == "text"), None)
    if text_block is None:
        raise RuntimeError("Claude API returned no text content")
    
    cleaned = text_block.text.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON from Claude API response: {text_block.text}") from e
    
    if "question" not in parsed or "answer" not in parsed:
        raise RuntimeError(f"Claude response missing question/answer fields: {text_block.text}")
    
    return GeneratedQuestion(
        question = parsed["question"],
        answer = parsed["answer"],
        sourceFile = file_path.name,
    )

#temporary to run
if __name__ == "__main__":
    question = generate_question()
    print(question)