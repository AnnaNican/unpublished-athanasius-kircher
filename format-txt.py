#!/usr/bin/env python3
"""
Format and clean text files extracted from PDFs.
Removes OCR artifacts, weird characters, and formatting issues.
Keeps only clean text in English, Latin, or Spanish.
"""

import sys
import re
from pathlib import Path
import unicodedata


def is_readable_char(char):
    """
    Check if a character is readable (letter, digit, or common punctuation).
    Supports English, Latin, and Spanish characters.
    
    Args:
        char: Character to check
        
    Returns:
        bool: True if character should be kept
    """
    # Allow Unicode categories: letters, digits, punctuation, symbols
    category = unicodedata.category(char)
    
    # Letters and digits
    if category.startswith('L') or category.startswith('N'):
        return True
    
    # Common punctuation and symbols for English/Latin/Spanish
    allowed_punct = set(".,;:!?()[]{}\"'-–—/\\*@#$%&+=")
    if char in allowed_punct:
        return True
    
    # Whitespace characters (space, tab, newline)
    if char.isspace():
        return True
    
    return False


def clean_text_line(line):
    """
    Clean a single line of text.
    
    Args:
        line: Line of text to clean
        
    Returns:
        str: Cleaned line, or None if line should be removed
    """
    # Remove control characters and non-printable characters
    line = ''.join(char for char in line if is_readable_char(char))
    
    # Normalize whitespace - replace multiple spaces with single space
    line = re.sub(r' +', ' ', line)
    
    # Remove leading/trailing whitespace
    line = line.strip()
    
    # Skip empty lines (they'll be handled separately)
    if not line:
        return None
    
    # Skip lines that are mostly punctuation or symbols
    char_count = len(line)
    letter_count = sum(1 for c in line if c.isalpha())
    if char_count > 0 and letter_count / char_count < 0.3:
        return None
    
    # Skip very short lines with mostly special characters (likely OCR artifacts)
    if char_count <= 5 and letter_count < char_count * 0.5:
        return None
    
    return line


def is_gibberish_line(line):
    """
    Check if a line is mostly gibberish (OCR artifact).
    
    Args:
        line: Line to check
        
    Returns:
        bool: True if line appears to be gibberish
    """
    if not line:
        return True
    
    # Remove whitespace for analysis
    text = line.replace(' ', '')
    if len(text) < 3:
        return True
    
    # Check ratio of letters to total characters
    letters = sum(1 for c in text if c.isalpha())
    if len(text) > 0 and letters / len(text) < 0.5:
        return True
    
    # Check for excessive punctuation or special characters
    punct = sum(1 for c in text if not c.isalnum() and not c.isspace())
    if len(text) > 0 and punct / len(text) > 0.4:
        return True
    
    # Check for patterns that suggest OCR errors
    # Multiple consecutive special characters
    if re.search(r'[^a-zA-Z0-9\s]{3,}', text):
        return True
    
    # Too many isolated characters (single chars separated by spaces)
    words = line.split()
    isolated = sum(1 for word in words if len(word) == 1 and not word.isalnum())
    if len(words) > 5 and isolated / len(words) > 0.5:
        return True
    
    return False


def clean_text_content(text):
    """
    Clean entire text content.
    
    Args:
        text: Full text content
        
    Returns:
        str: Cleaned text
    """
    lines = text.split('\n')
    cleaned_lines = []
    prev_line_empty = False
    
    for line in lines:
        # Keep page markers but clean them
        if line.strip().startswith('--- Page'):
            cleaned_line = re.sub(r'---\s*Page\s*\d+\s*---', f'--- Page {len(cleaned_lines) + 1} ---', line.strip())
            cleaned_lines.append(cleaned_line)
            prev_line_empty = False
            continue
        
        # Clean the line
        cleaned_line = clean_text_line(line)
        
        # Skip None or empty lines (but allow one blank line between paragraphs)
        if cleaned_line is None:
            if not prev_line_empty and cleaned_lines:
                # Allow one blank line for paragraph separation
                cleaned_lines.append('')
                prev_line_empty = True
            continue
        
        # Skip gibberish lines
        if is_gibberish_line(cleaned_line):
            continue
        
        # Add cleaned line
        cleaned_lines.append(cleaned_line)
        prev_line_empty = False
    
    # Join lines and clean up excessive blank lines
    result = '\n'.join(cleaned_lines)
    
    # Replace 3+ consecutive newlines with 2 newlines (paragraph break)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    # Remove leading/trailing whitespace
    result = result.strip()
    
    return result


def main():
    # Get the knowledge folder paths
    script_dir = Path(__file__).parent
    knowledge_dir = script_dir / "knowledge"
    txt_dir = knowledge_dir / "txt"
    txt_cleaned_dir = knowledge_dir / "txt-cleaned"
    
    if not knowledge_dir.exists():
        print(f"Error: Knowledge folder not found at {knowledge_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not txt_dir.exists():
        print(f"Error: Text folder not found at {txt_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Create cleaned text directory
    txt_cleaned_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all text files
    txt_files = sorted(list(txt_dir.glob("*.txt")) + list(txt_dir.glob("*.TXT")))
    
    if not txt_files:
        print(f"No text files found in {txt_dir}")
        return
    
    print(f"Found {len(txt_files)} text file(s) in knowledge/txt folder")
    print("-" * 50)
    
    processed_count = 0
    error_count = 0
    
    # Process each text file
    for txt_file in txt_files:
        print(f"\nProcessing: {txt_file.name}")
        
        try:
            # Read the text file
            with open(txt_file, "r", encoding="utf-8", errors='ignore') as f:
                original_text = f.read()
            
            if not original_text.strip():
                print(f"  ⚠ Warning: File is empty")
                continue
            
            original_size = len(original_text)
            original_lines = len(original_text.split('\n'))
            
            # Clean the text
            cleaned_text = clean_text_content(original_text)
            
            cleaned_size = len(cleaned_text)
            cleaned_lines = len(cleaned_text.split('\n'))
            
            # Save cleaned text
            output_file = txt_cleaned_dir / txt_file.name
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
            
            # Calculate reduction
            size_reduction = ((original_size - cleaned_size) / original_size * 100) if original_size > 0 else 0
            line_reduction = ((original_lines - cleaned_lines) / original_lines * 100) if original_lines > 0 else 0
            
            print(f"  ✓ Cleaned and saved")
            print(f"    Original: {original_size:,} chars, {original_lines:,} lines")
            print(f"    Cleaned:  {cleaned_size:,} chars, {cleaned_lines:,} lines")
            print(f"    Reduction: {size_reduction:.1f}% chars, {line_reduction:.1f}% lines")
            print(f"    Saved to: {output_file.name}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"  ✗ Error processing file: {str(e)}")
            error_count += 1
    
    # Print final summary
    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  - Successfully processed: {processed_count}")
    print(f"  - Errors: {error_count}")
    print(f"\nCleaned files saved to: {txt_cleaned_dir}")


if __name__ == "__main__":
    main()

