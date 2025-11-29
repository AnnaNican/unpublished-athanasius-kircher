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
import time
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv


STYLE_GUIDE_PATH = Path("kircker-style.md")
OUTPUT_PATH = Path("unpublished-kircher.md")
MODEL_NAME = "claude-sonnet-4-20250514"
DEFAULT_WORD_TARGET = 50000

# API limits: max_tokens controls output length
# Rough conversion: 1 token ≈ 0.75 words, so 8000 tokens ≈ 6000 words
# Claude Sonnet 4 supports up to 200,000 output tokens
MAX_TOKENS_PER_CHUNK = 8000  # Safe chunk size to avoid hitting limits
WORDS_PER_CHUNK = 6000  # Approximate words per chunk (8000 tokens * 0.75)


def read_style_guide() -> str:
    """Load the Kircher style document so it can be referenced in the prompt."""
    if not STYLE_GUIDE_PATH.exists():
        raise FileNotFoundError(
            f"Missing style guide at {STYLE_GUIDE_PATH}. "
            "Run extract_style.py first to generate it."
        )
    return STYLE_GUIDE_PATH.read_text(encoding="utf-8")


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def build_prompt(
    topic: str,
    word_target: int,
    style_guide: str,
    chunk_num: Optional[int] = None,
    total_chunks: Optional[int] = None,
    previous_text: Optional[str] = None,
) -> str:
    """Compose the system/user instructions for Claude."""
    continuation_note = ""
    if chunk_num is not None and total_chunks is not None:
        if chunk_num == 1:
            continuation_note = f"\n\nThis is the first of {total_chunks} sections. Begin the work with an appropriate opening."
        elif chunk_num == total_chunks:
            continuation_note = f"\n\nThis is the final section ({chunk_num} of {total_chunks}). Provide a satisfying conclusion that ties the entire work together."
        else:
            continuation_note = f"\n\nThis is section {chunk_num} of {total_chunks}. Continue seamlessly from where the previous section ended."
        
        if previous_text:
            # Include last paragraph of previous text for continuity
            prev_lines = previous_text.strip().split('\n')
            last_paragraph = prev_lines[-1] if prev_lines else ""
            continuation_note += f"\n\nPrevious section ended with:\n{last_paragraph}\n\nContinue from here naturally."
    
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
{continuation_note}
""".strip()


def call_claude(
    prompt: str,
    client: anthropic.Anthropic,
    max_tokens: int = MAX_TOKENS_PER_CHUNK,
) -> str:
    """Invoke Claude with parameters tuned for deliberate reasoning."""
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=max_tokens,
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


def generate_in_chunks(
    topic: str,
    word_target: int,
    style_guide: str,
    client: anthropic.Anthropic,
) -> str:
    """Generate text in chunks if target word count is large."""
    # Calculate number of chunks needed
    num_chunks = max(1, (word_target + WORDS_PER_CHUNK - 1) // WORDS_PER_CHUNK)
    words_per_chunk = word_target // num_chunks
    
    print(f"Target: {word_target:,} words")
    print(f"Generating in {num_chunks} chunk(s) of ~{words_per_chunk:,} words each...")
    print("-" * 50)
    
    all_chunks = []
    current_word_count = 0
    
    for chunk_idx in range(1, num_chunks + 1):
        print(f"\nGenerating chunk {chunk_idx}/{num_chunks}...")
        
        # Build prompt for this chunk
        previous_text = "\n\n".join(all_chunks) if all_chunks else None
        prompt = build_prompt(
            topic=topic,
            word_target=words_per_chunk,
            style_guide=style_guide,
            chunk_num=chunk_idx,
            total_chunks=num_chunks,
            previous_text=previous_text,
        )
        
        # Generate chunk
        try:
            chunk_text = call_claude(prompt, client, max_tokens=MAX_TOKENS_PER_CHUNK)
            chunk_words = count_words(chunk_text)
            all_chunks.append(chunk_text)
            current_word_count += chunk_words
            print(f"  ✓ Generated {chunk_words:,} words (total: {current_word_count:,}/{word_target:,})")
        except Exception as e:
            print(f"  ✗ Error generating chunk {chunk_idx}: {e}")
            raise
        
        # Rate limiting between chunks
        if chunk_idx < num_chunks:
            time.sleep(2)
    
    # Combine all chunks
    full_text = "\n\n".join(all_chunks)
    final_word_count = count_words(full_text)
    
    # If we're still short, generate additional chunks
    while final_word_count < word_target:
        remaining_words = word_target - final_word_count
        print(f"\nStill {remaining_words:,} words short. Generating additional chunk...")
        
        prompt = build_prompt(
            topic=topic,
            word_target=min(remaining_words + 500, WORDS_PER_CHUNK),  # Add buffer
            style_guide=style_guide,
            chunk_num=len(all_chunks) + 1,
            total_chunks=None,  # Continuation chunk
            previous_text=full_text,
        )
        
        try:
            additional_chunk = call_claude(prompt, client, max_tokens=MAX_TOKENS_PER_CHUNK)
            chunk_words = count_words(additional_chunk)
            all_chunks.append(additional_chunk)
            full_text = "\n\n".join(all_chunks)
            final_word_count = count_words(full_text)
            print(f"  ✓ Generated {chunk_words:,} words (total: {final_word_count:,}/{word_target:,})")
        except Exception as e:
            print(f"  ✗ Error generating additional chunk: {e}")
            break
        
        time.sleep(2)
    
    return full_text


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
    
    # Use chunking for large word counts
    if args.words > WORDS_PER_CHUNK:
        print("Large word count detected. Using chunked generation...")
        draft_text = generate_in_chunks(args.topic, args.words, style_text, client)
    else:
        # Single generation for smaller targets
        prompt = build_prompt(args.topic, args.words, style_text)
        draft_text = call_claude(prompt, client, max_tokens=MAX_TOKENS_PER_CHUNK)
    
    # Verify word count before saving
    final_word_count = count_words(draft_text)
    print("\n" + "=" * 50)
    print(f"Final word count: {final_word_count:,} words")
    print(f"Target: {args.words:,} words")
    
    if final_word_count < args.words:
        print(f"⚠ Warning: Generated text is {args.words - final_word_count:,} words short of target.")
        response = input("Save anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Aborted. Text not saved.")
            return
    
    args.output.write_text(draft_text.strip() + "\n", encoding="utf-8")
    print(f"✓ Wrote {args.output} ({final_word_count:,} words).")


if __name__ == "__main__":
    main()


