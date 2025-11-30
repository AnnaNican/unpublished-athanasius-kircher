#!/usr/bin/env python3
"""
supplementary-metadata.py
-------------------------

Extract bibliography from page 94 of the Godwin book and format as markdown table.
Also extract all images from the PDF and save them to knowledge/images/.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF


# Paths relative to project root (go up one level from extract-text/)
SCRIPT_DIR = Path(__file__).parent.parent
SUPPLEMENTARY_DIR = SCRIPT_DIR / "knowledge" / "supplementary"
IMAGES_DIR = SCRIPT_DIR / "knowledge" / "images"
BIBLIOGRAPHY_PAGE = 94
PDF_FILENAME = "Godwin Joscelyn - Athanasius Kircher A renaissance man and the quest for lost knowledge.pdf"


def extract_page_text(pdf_path: Path, page_num: int, use_ocr: bool = False) -> str:
    """
    Extract text from a specific page of a PDF.
    
    Args:
        pdf_path: Path to PDF file
        page_num: Page number (1-indexed)
        use_ocr: If True, attempt OCR for image-based pages
        
    Returns:
        str: Extracted text from the page
    """
    try:
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            raise ValueError(f"Page {page_num} is out of range (1-{len(doc)})")
        
        page = doc[page_num - 1]  # Convert to 0-indexed
        
        # Try standard text extraction first
        text = page.get_text()
        
        # If no text found and OCR is requested, try OCR
        if not text.strip() and use_ocr:
            try:
                # PyMuPDF OCR (requires tesseract)
                text = page.get_text("ocr")
            except Exception:
                # Fallback: try different text extraction method
                text = page.get_text("text")
        
        # If still no text, try getting text blocks
        if not text.strip():
            text_dict = page.get_text("dict")
            text_parts = []
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text_parts.append(span.get("text", ""))
            text = "\n".join(text_parts)
        
        doc.close()
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from page {page_num}: {e}")


def parse_bibliography(text: str) -> list[dict[str, str]]:
    """
    Parse bibliography text into structured entries.
    
    Expected format variations:
    - "Title (Year). Description"
    - "Title, Year. Description"
    - "Title. Year. Description"
    - "Title | Year Description" (alternative format)
    
    Args:
        text: Raw bibliography text
        
    Returns:
        list: List of dicts with 'title', 'year', 'description' keys
    """
    entries = []
    lines = text.split('\n')
    
    current_entry = None
    
    for line in lines:
        line = line.strip()
        if not line:
            # Empty line might indicate end of current entry
            if current_entry:
                entries.append(current_entry)
                current_entry = None
            continue
        
        # Skip headers and section markers
        if line.startswith('#') or line.startswith('*') and 'Bibliography' in line:
            continue
        
        # Try to match bibliography entry patterns
        # Pattern 1: "Title (Year). Description"
        match1 = re.match(r'^(.+?)\s*\((\d{4})\)\.?\s*(.+)$', line)
        # Pattern 2: "Title, Year. Description"
        match2 = re.match(r'^(.+?),\s*(\d{4})\.\s*(.+)$', line)
        # Pattern 3: "Title. Year. Description"
        match3 = re.match(r'^(.+?\.)\s*(\d{4})\.\s*(.+)$', line)
        # Pattern 4: "Title | Year Description" (alternative format)
        match4 = re.match(r'^(.+?)\s*\|\s*(\d{4})\s+(.+)$', line)
        # Pattern 5: Just title and year, description might be on next line
        match5 = re.match(r'^(.+?)\s*\((\d{4})\)\.?$', line)
        # Pattern 6: "Title Year Description" (no punctuation)
        match6 = re.match(r'^(.+?)\s+(\d{4})\s+(.+)$', line)
        
        if match1:
            title, year, desc = match1.groups()
            if current_entry:
                entries.append(current_entry)
            entries.append({
                'title': title.strip(),
                'year': year.strip(),
                'description': desc.strip()
            })
            current_entry = None
        elif match2:
            title, year, desc = match2.groups()
            if current_entry:
                entries.append(current_entry)
            entries.append({
                'title': title.strip(),
                'year': year.strip(),
                'description': desc.strip()
            })
            current_entry = None
        elif match3:
            title, year, desc = match3.groups()
            if current_entry:
                entries.append(current_entry)
            entries.append({
                'title': title.strip(),
                'year': year.strip(),
                'description': desc.strip()
            })
            current_entry = None
        elif match4:
            title, year, desc = match4.groups()
            if current_entry:
                entries.append(current_entry)
            entries.append({
                'title': title.strip(),
                'year': year.strip(),
                'description': desc.strip()
            })
            current_entry = None
        elif match5:
            # Title and year, description might be on next line
            if current_entry:
                entries.append(current_entry)
            title, year = match5.groups()
            current_entry = {
                'title': title.strip(),
                'year': year.strip(),
                'description': ''
            }
        elif match6:
            # Try to extract if it looks like a bibliography entry
            title, year, desc = match6.groups()
            if len(year) == 4 and year.isdigit():
                if current_entry:
                    entries.append(current_entry)
                entries.append({
                    'title': title.strip(),
                    'year': year.strip(),
                    'description': desc.strip()
                })
                current_entry = None
            else:
                # Might be continuation
                if current_entry:
                    current_entry['description'] += ' ' + line
                elif entries:
                    entries[-1]['description'] += ' ' + line
        else:
            # Might be continuation of previous entry
            if current_entry:
                if current_entry['description']:
                    current_entry['description'] += ' ' + line
                else:
                    current_entry['description'] = line
            elif entries:
                # Add as continuation of last entry
                if entries[-1]['description']:
                    entries[-1]['description'] += ' ' + line
                else:
                    entries[-1]['description'] = line
    
    # Add current_entry if exists
    if current_entry:
        entries.append(current_entry)
    
    # Clean up descriptions
    for entry in entries:
        entry['description'] = entry['description'].strip()
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
        return "No bibliography entries found."
    
    # Create markdown table
    lines = ["# Bibliography", "", "| Title | Year | Description |", "|-------|------|-------------|"]
    
    for entry in entries:
        # Escape pipe characters in content
        title = entry['title'].replace('|', '\\|')
        year = entry['year']
        desc = entry['description'].replace('|', '\\|').replace('\n', ' ')
        
        # Truncate very long descriptions for readability
        if len(desc) > 200:
            desc = desc[:197] + "..."
        
        lines.append(f"| {title} | {year} | {desc} |")
    
    return "\n".join(lines)


def extract_images(pdf_path: Path, output_dir: Path) -> list[str]:
    """
    Extract all images from PDF and save them to output directory.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save images
        
    Returns:
        list: List of saved image filenames
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_images = []
    doc = fitz.open(pdf_path)
    
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Generate filename
                img_filename = f"page_{page_num + 1:03d}_img_{img_index + 1:02d}.{image_ext}"
                img_path = output_dir / img_filename
                
                # Save image
                with open(img_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                saved_images.append(img_filename)
                print(f"  ✓ Extracted: {img_filename} (from page {page_num + 1})")
    
    finally:
        doc.close()
    
    return saved_images


def main() -> None:
    """Main function."""
    pdf_path = SUPPLEMENTARY_DIR / PDF_FILENAME
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing: {PDF_FILENAME}")
    print("=" * 60)
    
    # Extract bibliography from page 94
    print(f"\nExtracting bibliography from page {BIBLIOGRAPHY_PAGE}...")
    try:
        # Try with OCR first if available
        page_text = extract_page_text(pdf_path, BIBLIOGRAPHY_PAGE, use_ocr=True)
        print(f"  ✓ Extracted {len(page_text)} characters")
        
        if not page_text.strip():
            print(f"  ⚠ Warning: No text found on page {BIBLIOGRAPHY_PAGE}")
            print(f"  This page may be image-only. Check the extracted image:")
            print(f"    {IMAGES_DIR / f'page_{BIBLIOGRAPHY_PAGE:03d}_img_01.png'}")
            print(f"  You may need to use OCR or manually extract the bibliography.")
            # Create placeholder
            entries = []
        else:
            # Parse bibliography
            entries = parse_bibliography(page_text)
            print(f"  ✓ Parsed {len(entries)} bibliography entries")
        
        # Format as markdown table
        markdown_table = format_bibliography_table(entries)
        
        # Save bibliography
        bib_output = SCRIPT_DIR / "kircher-bibliography.md"
        bib_output.write_text(markdown_table, encoding="utf-8")
        print(f"  ✓ Saved bibliography to: {bib_output.name}")
        
        # Also print first few entries for verification
        if entries:
            print(f"\n  Sample entries:")
            for i, entry in enumerate(entries[:3], 1):
                print(f"    {i}. {entry['title']} ({entry['year']})")
        else:
            print(f"\n  Note: No entries parsed. The page may require manual extraction or OCR.")
        
    except Exception as e:
        print(f"  ✗ Error extracting bibliography: {e}", file=sys.stderr)
        # Don't exit - continue with image extraction
        print(f"  Continuing with image extraction...")
    
    # Extract all images
    print(f"\nExtracting images from PDF...")
    try:
        saved_images = extract_images(pdf_path, IMAGES_DIR)
        print(f"  ✓ Extracted {len(saved_images)} images to {IMAGES_DIR}")
    except Exception as e:
        print(f"  ✗ Error extracting images: {e}", file=sys.stderr)
        # Don't exit, bibliography extraction succeeded
    
    print("\n" + "=" * 60)
    print("✓ Processing complete!")


if __name__ == "__main__":
    main()

