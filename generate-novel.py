#!/usr/bin/env python3
"""
generate-novel.py
-----------------

Utility script that asks Anthropic's Claude model to produce fresh prose
that mirrors Athanasius Kircher's style guidelines captured in
`kircker-style.md`.  Pass an optional topic prompt and a target word-count
to influence the output.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv


STYLE_GUIDE_PATH = Path("kircker-style.md")
OUTPUT_PATH = Path("unpublished-kircher.md")
MODEL_NAME = "claude-sonnet-4-20250514"
DEFAULT_WORD_TARGET = 1200


def read_style_guide() -> str:
    """Load the Kircher style document so it can be referenced in the prompt."""
    if not STYLE_GUIDE_PATH.exists():
        raise FileNotFoundError(
            f"Missing style guide at {STYLE_GUIDE_PATH}. "
            "Run extract_style.py first to generate it."
        )
    return STYLE_GUIDE_PATH.read_text(encoding="utf-8")


def build_prompt(topic: str, word_target: int, style_guide: str) -> str:
    """Compose the system/user instructions for Claude."""
    return f"""
You are Athanasius Kircher's literary apprentice. Study the following style guide and
write a new passage that could plausibly appear in one of his manuscripts.

STYLE GUIDE (verbatim excerpt from kircker-style.md):
----------------------------------------
{style_guide}
----------------------------------------

TASK:
- Compose approximately {word_target} words of original prose.
- Topic / seed idea: {topic or "Author's choice — stay within Kircher's typical themes."}
- Preserve the rhetorical flair, sentence architecture, and tonal qualities described above.
- Avoid directly copying phrases from the guide; synthesize fresh text.
- Close with a short reflective coda that ties the piece back to natural philosophy.
""".strip()


def call_claude(prompt: str, client: anthropic.Anthropic) -> str:
    """Invoke Claude with parameters tuned for deliberate reasoning."""
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=4096,
        temperature=1.0,
        top_p=0.95,
        thinking={"type": "enabled", "budget_tokens": 2048},
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    )
    text_chunks = []
    for block in response.content:
        block_text = getattr(block, "text", None)
        if block_text:
            text_chunks.append(block_text.strip())
    if not text_chunks:
        raise RuntimeError("Claude response contained no text blocks.")
    return "\n\n".join(text_chunks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Kircher-style prose via Claude.")
    parser.add_argument(
        "--words",
        type=int,
        default=DEFAULT_WORD_TARGET,
        help=f"Approximate word target for the output (default: {DEFAULT_WORD_TARGET}).",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="",
        help="Optional topic/seed idea to anchor the generated text.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help=f"Destination file for the generated prose (default: {OUTPUT_PATH}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ANTHROPIC_API_KEY in environment or .env file.")

    client = anthropic.Anthropic(api_key=api_key)
    style_text = read_style_guide()
    prompt = build_prompt(args.topic, args.words, style_text)
    draft_text = call_claude(prompt, client)
    args.output.write_text(draft_text.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.output} (target ≈{args.words} words).")


if __name__ == "__main__":
    main()


