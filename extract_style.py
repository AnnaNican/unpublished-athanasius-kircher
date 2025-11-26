"""Utility to load a knowledge file and send it to Anthropic's Claude Sonnet."""

import os
import time
from pathlib import Path
from typing import List

import anthropic
from dotenv import load_dotenv


KNOWLEDGE_PATHS = [
    Path("knowledge/txt-en/societate-lesu-arithmologia.txt"),
    Path("knowledge/txt-en/ars-magna-lucis.txt"),
]
OUTPUT_PATH = Path("kircker-style.md")
CHUNK_SIZE = 20_000
CHUNK_DELAY_SECONDS = 60
MAX_CHUNKS = 10
PROMPT_TEXT = """
I'm working on a creative writing project where I want to understand and potentially
emulate the writing style of this book. Please analyze the attached text and create
a detailed style guide that captures:

**1. PROSE STYLE & MECHANICS**

- Sentence structure: Are sentences typically short/long? Simple or complex?
- Paragraph length and rhythm
- Use of punctuation (em dashes, semicolons, ellipses, etc.)
- Vocabulary level: formal, colloquial, archaic, technical?
- Distinctive word choices or recurring phrases
- Use of literary devices (metaphors, similes, alliteration, etc.)

**2. NARRATIVE VOICE & TONE**

- Point of view (first/third person, omniscient, limited, etc.)
- Narrative distance: intimate or detached?
- Overall tone: serious, humorous, ironic, melancholic, etc.
- How does the narrator address the reader (if at all)?

**3. PACING & STRUCTURE**

- Balance of dialogue vs. description vs. action
- How are scenes transitioned?
- Pacing: contemplative and slow, or fast-moving?
- Use of flashbacks, time jumps, or non-linear structure

**4. THEMATIC ELEMENTS**

- Major themes explored
- Recurring symbols or motifs
- Philosophical or moral perspectives presented
- Types of conflicts (internal, interpersonal, societal, etc.)

**5. DISTINCTIVE STYLISTIC FINGERPRINTS**

- What makes this author's voice unique and recognizable?
- Signature techniques or patterns
- Things this author does that others typically don't

Please provide specific examples from the text to illustrate each point. Format
this as a practical style guide I can reference when writing in a similar style.
""".strip()


def load_knowledge() -> str:
    """Read the first existing knowledge file and return its contents."""
    for candidate in KNOWLEDGE_PATHS:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    raise FileNotFoundError(
        "None of the expected knowledge files exist: "
        + ", ".join(str(p) for p in KNOWLEDGE_PATHS)
    )


def split_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split text into roughly `chunk_size`-character chunks."""
    words = text.split()
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_size = 0

    for word in words:
        current_size += len(word) + 1  # include spacing cost
        if current_size > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def main() -> None:
    """Instantiate the Anthropic client, run the prompt, and save the output."""
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ANTHROPIC_API_KEY in environment or .env file.")

    client = anthropic.Anthropic(api_key=api_key)
    knowledge_text = load_knowledge()
    chunks = split_text(knowledge_text, CHUNK_SIZE)[:MAX_CHUNKS]

    chunk_outputs: List[str] = []
    for idx, chunk in enumerate(chunks):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT_TEXT},
                        {
                            "type": "text",
                            "text": f"[Chunk {idx + 1}/{len(chunks)}]\n\n{chunk}",
                        },
                    ],
                }
            ],
        )
        chunk_outputs.append(f"## Chunk {idx + 1}\n\n{response.content[0].text}")

        if idx < len(chunks) - 1:
            time.sleep(CHUNK_DELAY_SECONDS)

    OUTPUT_PATH.write_text("\n\n".join(chunk_outputs), encoding="utf-8")


if __name__ == "__main__":
    main()

