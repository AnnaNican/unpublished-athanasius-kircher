#!/usr/bin/env python3
"""
extract_bibliography_from_image.py
-----------------------------------

Extract bibliography from page_095_img_01.png image and format as markdown table.
Uses OCR to extract text, then parses it into structured bibliography entries.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Try Claude API for image OCR (vision capabilities)
try:
    import anthropic
    import base64
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

# Also import dotenv and os at module level
from dotenv import load_dotenv
import os


# Paths relative to project root (go up one level from extract-text/)
SCRIPT_DIR = Path(__file__).parent.parent
IMAGES_DIR = SCRIPT_DIR / "knowledge" / "images"
IMAGE_FILENAME = "page_095_img_01.png"
OUTPUT_FILE = SCRIPT_DIR / "kircher-bibliography.md"


def extract_text_from_image(image_path: Path) -> str:
    """
    Extract text from an image using OCR (pytesseract or Unstructured API).
    
    Args:
        image_path: Path to image file
        
    Returns:
        str: Extracted text
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Try pytesseract first
    if OCR_AVAILABLE:
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='eng')
            return text
        except Exception as e:
            print(f"  Warning: pytesseract failed: {e}", file=sys.stderr)
            print("  Trying Unstructured API as fallback...", file=sys.stderr)
    
    # Fallback to Claude API (vision)
    if CLAUDE_AVAILABLE:
        try:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY not found in environment")
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine image MIME type
            if image_path.suffix.lower() == '.png':
                media_type = 'image/png'
            elif image_path.suffix.lower() in ['.jpg', '.jpeg']:
                media_type = 'image/jpeg'
            else:
                media_type = 'image/png'  # Default
            
            # Use Claude to extract text from image
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": "Extract all text from this bibliography page. Preserve the exact formatting, including titles, publication locations, years, and descriptions. Return the text exactly as it appears."
                            }
                        ]
                    }
                ]
            )
            
            # Extract text from response
            text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    text += block.text
            
            return text
            
        except Exception as e:
            raise RuntimeError(f"Error extracting text with Claude API: {e}")
    
    # No OCR available
    raise RuntimeError(
        "No OCR method available. Please install one of:\n"
        "  - pytesseract: pip install pytesseract pillow && brew install tesseract\n"
        "  - Or set ANTHROPIC_API_KEY in .env file (for Claude vision API)"
    )


def parse_bibliography_entries(text: str) -> list[dict[str, str]]:
    """
    Parse bibliography text into structured entries.
    
    Expected format: Title (Location Year). Description
    Or: Title (Location, Year). Description
    
    Args:
        text: Raw OCR text
        
    Returns:
        list: List of dicts with 'title', 'location', 'year', 'description' keys
    """
    entries = []
    
    # Split by lines first to preserve structure
    lines = text.split('\n')
    
    current_entry = None
    
    for line in lines:
        line = line.strip()
        if not line:
            # Empty line might end current entry
            if current_entry:
                entries.append(current_entry)
                current_entry = None
            continue
        
        # Skip headers
        if line.upper() in ['SELECT BIBLIOGRAPHY', "KIRCHER'S WRITINGS", 'I KIRCHER\'S WRITINGS', 
                           'II WRITINGS, ETC.,', 'EDITED BY OTHERS', 'WRITINGS, ETC., EDITED BY OTHERS']:
            if current_entry:
                entries.append(current_entry)
                current_entry = None
            continue
        
        # Pattern 1: Title (Location Year). Description
        # Pattern 2: Title (Location, Year). Description
        # Pattern 3: Title (Location Year; Location Year). Description (multiple editions)
        # Pattern 4: Title (Location Year, Year). Description
        
        # Try to match: Title (Location Year). or Title (Location, Year).
        # First, try to find the first occurrence of (Location Year) pattern
        paren_match = re.search(r'\(([^)]+)\)', line)
        if paren_match:
            paren_content = paren_match.group(1)
            title = line[:paren_match.start()].strip()
            description = line[paren_match.end():].strip()
            
            # Extract first location and year from parentheses
            # Pattern: Location Year or Location, Year or Location Year; Location Year
            # Find first 4-digit year
            year_match = re.search(r'(\d{4})', paren_content)
            if year_match:
                year = year_match.group(1)
                # Get location (everything before the first year)
                location_part = paren_content[:year_match.start()].strip()
                # Clean up location - remove trailing semicolons, commas
                location = re.sub(r'[;,]\s*$', '', location_part).strip()
                
                # If location is empty or just numbers, try to get it differently
                if not location or location.isdigit():
                    # Try to extract location before year (might be "Location Year" format)
                    parts = paren_content.split()
                    location = ""
                    for i, part in enumerate(parts):
                        if part.isdigit() and len(part) == 4:
                            # Found year, location is everything before it
                            location = ' '.join(parts[:i]).strip()
                            break
                
                # Clean up title
                title = re.sub(r'^[•\-\*]\s*', '', title)
                title = title.strip()
                
                # Clean up description (remove leading period)
                description = re.sub(r'^\.\s*', '', description).strip()
                
                if current_entry:
                    entries.append(current_entry)
                
                current_entry = {
                    'title': title,
                    'location': location if location else 'n.p.',
                    'year': year,
                    'description': description
                }
            else:
                # No year found, might be continuation
                if current_entry:
                    current_entry['description'] += ' ' + line
        else:
            # No parentheses found, might be continuation
            if current_entry:
                current_entry['description'] += ' ' + line
    
    # Add last entry
    if current_entry:
        entries.append(current_entry)
    
    # Clean up entries
    for entry in entries:
        entry['title'] = entry['title'].strip()
        entry['location'] = entry['location'].strip()
        entry['year'] = entry['year'].strip()
        entry['description'] = entry['description'].strip()
        
        # Remove trailing periods from description if it's just punctuation
        if entry['description'] and entry['description'].endswith('.'):
            # Keep the period if it's part of the description
            pass
        
        if not entry['description']:
            entry['description'] = 'No description available'
    
    return entries


def format_bibliography_table(entries: list[dict[str, str]]) -> str:
    """
    Format bibliography entries as a markdown table.
    
    Args:
        entries: List of bibliography entry dicts
        
    Returns:
        str: Markdown formatted table
    """
    if not entries:
        return "# Bibliography\n\nNo entries found.\n"
    
    # Create markdown table
    lines = [
        "# Bibliography of Athanasius Kircher's Works",
        "",
        "| Title | Year | Location | Description |",
        "|-------|------|----------|-------------|"
    ]
    
    for entry in entries:
        # Escape pipe characters in content
        title = entry['title'].replace('|', '\\|').replace('\n', ' ')
        year = entry['year']
        location = entry['location'].replace('|', '\\|').replace('\n', ' ')
        desc = entry['description'].replace('|', '\\|').replace('\n', ' ')
        
        # Truncate very long descriptions for readability
        if len(desc) > 300:
            desc = desc[:297] + "..."
        if len(title) > 150:
            title = title[:147] + "..."
        
        lines.append(f"| {title} | {year} | {location} | {desc} |")
    
    return "\n".join(lines)


def main() -> None:
    """Main function."""
    image_path = IMAGES_DIR / IMAGE_FILENAME
    
    if not image_path.exists():
        print(f"Error: Image not found at {image_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Extracting bibliography from: {IMAGE_FILENAME}")
    print("=" * 60)
    
    # Extract text using OCR
    print("\nExtracting text using OCR...")
    try:
        text = extract_text_from_image(image_path)
        print(f"  ✓ Extracted {len(text)} characters")
        
        # Save raw OCR text for debugging
        debug_file = SCRIPT_DIR / "bibliography-ocr-raw.txt"
        debug_file.write_text(text, encoding="utf-8")
        print(f"  ✓ Saved raw OCR text to: {debug_file.name}")
        
    except Exception as e:
        print(f"  ✗ Error extracting text: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse bibliography entries
    print("\nParsing bibliography entries...")
    try:
        entries = parse_bibliography_entries(text)
        print(f"  ✓ Parsed {len(entries)} bibliography entries")
        
        if not entries:
            print("\n  ⚠ Warning: No entries were parsed.")
            print(f"  Check the raw OCR text in: {debug_file.name}")
            print("  You may need to manually adjust the parsing logic.")
        else:
            # Print sample entries for verification
            print(f"\n  Sample entries:")
            for i, entry in enumerate(entries[:3], 1):
                print(f"    {i}. {entry['title']} ({entry['location']}, {entry['year']})")
        
    except Exception as e:
        print(f"  ✗ Error parsing entries: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Format as markdown table
    print("\nFormatting as markdown table...")
    markdown_table = format_bibliography_table(entries)
    
    # Save to file
    OUTPUT_FILE.write_text(markdown_table, encoding="utf-8")
    print(f"  ✓ Saved bibliography to: {OUTPUT_FILE.name}")
    
    print("\n" + "=" * 60)
    print("✓ Processing complete!")
    if entries:
        print(f"  Total entries: {len(entries)}")


if __name__ == "__main__":
    main()

