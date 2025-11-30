#!/usr/bin/env python3
"""
Clean and normalize the English OCR dumps that live under knowledge/txt-en.

The script removes:
    - Residual page markers such as "--- Page 201 ---"
    - Broken line spacing where punctuation drifts onto its own line
    - OCR noise tokens made of repeated symbols or junk characters

It also collapses soft line breaks so that the final file contains
paragraph-sized blocks that are easy to read.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable


PAGE_RE = re.compile(r'\s*[-–—]{2,}\s*Page\s*\d+\s*[-–—]{0,}\s*', re.IGNORECASE)
REPEAT_CHAR_RE = re.compile(r'(.)\1{4,}', re.IGNORECASE)
SOFT_PUNCT_BREAK_RE = re.compile(r'\n+\s*([,.;:!?])')
WHITESPACE_CLUSTER_RE = re.compile(r'[^\S\n]+')
PARA_SPLIT_RE = re.compile(r'\n{2,}')
ROMAN_NUMERAL_CHARS = set('IVXLCDM')

# Use a sentinel that is unlikely to show up in historical text.
PARA_SENTINEL = '<<__PARA_BREAK__>>'


def clean_document(text: str) -> str:
    """Return a cleaned, paragraph-friendly version of the supplied text."""
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    normalized = PAGE_RE.sub('\n', normalized)

    # Remove silly breaks where punctuation was pushed to a new line.
    normalized = SOFT_PUNCT_BREAK_RE.sub(r'\1', normalized)

    # Remove all blank lines between text (3+ newlines become 2, then we'll remove all blank lines)
    normalized = re.sub(r'\n{3,}', '\n\n', normalized)
    normalized = normalized.replace('\u00a0', ' ')
    normalized = normalized.replace('\t', ' ')

    normalized = normalized.replace('\n\n', PARA_SENTINEL)
    normalized = normalized.replace('\n', ' ')
    normalized = WHITESPACE_CLUSTER_RE.sub(' ', normalized)
    normalized = normalized.replace(PARA_SENTINEL, '\n\n')

    paragraphs: Iterable[str] = PARA_SPLIT_RE.split(normalized)
    cleaned_paragraphs = []

    for raw in paragraphs:
        cleaned = clean_paragraph(raw)
        if cleaned:
            cleaned_paragraphs.append(cleaned)

    # Join paragraphs with single newline (remove blank lines between paragraphs)
    result = '\n'.join(cleaned_paragraphs).strip()
    
    # Remove any remaining blank lines (2+ consecutive newlines become single newline)
    result = re.sub(r'\n{2,}', '\n', result)
    
    # Remove lines that are entirely whitespace
    lines = result.split('\n')
    cleaned_lines = [line for line in lines if line.strip()]
    result = '\n'.join(cleaned_lines)
    
    return f"{result}\n" if result else ''


def clean_paragraph(paragraph: str) -> str:
    """Strip OCR artifacts from an individual paragraph."""
    paragraph = paragraph.strip()
    if not paragraph:
        return ''

    tokens = paragraph.split()
    filtered_tokens = []
    alpha_total = 0
    real_word_count = 0

    for token in tokens:
        core = token.strip(".,;:!?\"'()[]{}")

        if not core:
            # Pure punctuation – only keep meaningful sentence marks.
            if token in {'.', ',', ';', ':', '?', '!'}:
                filtered_tokens.append(token)
            continue

        if is_noise_token(core):
            continue

        filtered_tokens.append(token)
        letters_in_token = sum(1 for c in core if c.isalpha())
        alpha_total += letters_in_token
        if letters_in_token:
            real_word_count += 1

    if not filtered_tokens or real_word_count < 3 or alpha_total < 12:
        return ''

    paragraph = ' '.join(filtered_tokens)
    paragraph = re.sub(r'\s+([,.;:!?])', r'\1', paragraph)
    paragraph = re.sub(r'([,.;:!?])([^\s])', r'\1 \2', paragraph)
    paragraph = WHITESPACE_CLUSTER_RE.sub(' ', paragraph)
    paragraph = paragraph.strip()

    if not re.search(r'[.!?]', paragraph) and real_word_count < 12:
        return ''

    return paragraph


def is_noise_token(token: str) -> bool:
    """Heuristically determine whether a token looks like OCR junk."""
    if not token:
        return True

    letters = [c for c in token if c.isalpha()]
    digits = [c for c in token if c.isdigit()]
    specials = [c for c in token if not c.isalnum()]

    if not letters:
        return True

    if any(ch in token for ch in '*\\/|'):
        return True

    if specials and len(specials) / len(token) > 0.4:
        return True

    if len(set(token.lower())) <= 2 and len(token) >= 10:
        return True

    if REPEAT_CHAR_RE.search(token):
        return True

    if digits and len(digits) / len(token) > 0.6:
        return True

    has_vowel = any(ch.lower() in 'aeiouy' for ch in letters)
    if not has_vowel:
        upper_letters = set(ch.upper() for ch in letters)
        if not upper_letters.issubset(ROMAN_NUMERAL_CHARS):
            # Skip obvious consonant-mashed noise.
            if len(token) > 3:
                return True

    # Single-character Latin strings are usually abbreviations; keep them.
    return False


def collect_txt_files(root: Path) -> list[Path]:
    return sorted([p for p in root.glob('*.txt') if p.is_file()])


def main() -> None:
    script_dir = Path(__file__).resolve().parent.parent  # Go up one level from clean-text/
    target_dir = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else script_dir / 'knowledge' / 'txt-en'

    if not target_dir.exists():
        print(f"Error: directory not found -> {target_dir}", file=sys.stderr)
        sys.exit(1)

    txt_files = collect_txt_files(target_dir)
    if not txt_files:
        print(f"No .txt files found in {target_dir}")
        return

    print(f"Cleaning {len(txt_files)} file(s) inside {target_dir} ...")

    for file_path in txt_files:
        try:
            original = file_path.read_text(encoding='utf-8', errors='ignore')
            cleaned = clean_document(original)
            file_path.write_text(cleaned, encoding='utf-8')
            print(f"  ✓ {file_path.name}")
        except Exception as exc:
            print(f"  ✗ {file_path.name}: {exc}", file=sys.stderr)


if __name__ == '__main__':
    main()


