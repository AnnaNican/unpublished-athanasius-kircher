#!/usr/bin/env python3
"""
Extract text from all PDF files in the knowledge/pdf folder
and save the extracted text to knowledge/txt folder.
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        tuple: (success: bool, text_content: str or error_message: str)
    """
    try:
        doc = fitz.open(pdf_path)
        text_content = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_content.append(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
        return True, "\n\n".join(text_content)
    except Exception as e:
        return False, f"Error extracting text: {str(e)}"


def main():
    # Get the knowledge folder paths
    script_dir = Path(__file__).parent
    knowledge_dir = script_dir / "knowledge"
    pdf_dir = knowledge_dir / "pdf"
    txt_dir = knowledge_dir / "txt"
    
    if not knowledge_dir.exists():
        print(f"Error: Knowledge folder not found at {knowledge_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not pdf_dir.exists():
        print(f"Error: PDF folder not found at {pdf_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Create txt directory if it doesn't exist
    txt_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all PDF files (case-insensitive, including .PDF)
    pdf_files = sorted(list(pdf_dir.glob("*.pdf")) + list(pdf_dir.glob("*.PDF")))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) in knowledge/pdf folder")
    print("-" * 50)
    
    # Extract text from each PDF
    success_count = 0
    error_count = 0
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        
        # Extract text
        success, result = extract_text_from_pdf(pdf_file)
        
        if not success:
            print(f"  ✗ Failed: {result}")
            error_count += 1
            continue
        
        # Save to text file in txt folder
        output_file = txt_dir / f"{pdf_file.stem}.txt"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            
            # Print summary
            word_count = len(result.split())
            char_count = len(result)
            print(f"  ✓ Extracted {word_count:,} words ({char_count:,} characters)")
            print(f"  ✓ Saved to: {output_file.name}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ Failed to save file: {str(e)}", file=sys.stderr)
            error_count += 1
    
    # Print final summary
    print("\n" + "=" * 50)
    print(f"Summary: {success_count} successful, {error_count} failed")


if __name__ == "__main__":
    main()


