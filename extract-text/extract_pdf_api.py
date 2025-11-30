#!/usr/bin/env python3
"""
Extract text from all PDF files in the knowledge/pdf folder
using the Unstructured API and save the extracted text to knowledge/txt folder.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from unstructured_client import UnstructuredClient
from unstructured_client.models import operations, shared


def extract_text_from_pdf_api(pdf_path: Path, client: UnstructuredClient) -> tuple[bool, str]:
    """
    Extract text from a PDF file using the Unstructured API.
    
    Args:
        pdf_path: Path to the PDF file
        client: Initialized UnstructuredClient instance
        
    Returns:
        tuple: (success: bool, text_content: str or error_message: str)
    """
    try:
        # Read the PDF file
        with open(pdf_path, "rb") as f:
            file_content = f.read()
        
        # Create a Files object
        files = shared.Files(
            content=file_content,
            file_name=pdf_path.name
        )
        
        # Create a PartitionRequest
        # Using "text/plain" output format for simple text extraction
        request = operations.PartitionRequest(
            files=files,
            output_format="text/plain",
            strategy="hi_res",  # High resolution for better OCR quality
        )
        
        # Send the request to the Unstructured API
        response = client.partition(request)
        
        # Extract text from response
        # The response structure depends on the output format
        if hasattr(response, 'elements'):
            # If response has elements, concatenate their text
            text_parts = []
            for element in response.elements:
                if hasattr(element, 'text') and element.text:
                    text_parts.append(element.text)
            text_content = "\n\n".join(text_parts)
        elif hasattr(response, 'text'):
            text_content = response.text
        elif isinstance(response, str):
            text_content = response
        else:
            # Try to get text from response content
            text_content = str(response)
        
        return True, text_content
        
    except Exception as e:
        return False, f"Error extracting text: {str(e)}"


def main():
    """Main function to process all PDFs in knowledge/pdf folder."""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("UNSTRUCTURED_API_KEY")
    if not api_key:
        print("Error: UNSTRUCTURED_API_KEY not found in environment or .env file", file=sys.stderr)
        print("Please set UNSTRUCTURED_API_KEY in your .env file or environment variables.", file=sys.stderr)
        sys.exit(1)
    
    # Optional: Get API URL from environment (defaults to production if not set)
    api_url: Optional[str] = os.getenv("UNSTRUCTURED_API_URL")
    
    # Initialize the Unstructured client
    try:
        if api_url:
            client = UnstructuredClient(api_key_auth=api_key, server_url=api_url)
        else:
            client = UnstructuredClient(api_key_auth=api_key)
    except Exception as e:
        print(f"Error initializing Unstructured client: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Get the knowledge folder paths (go up one level from extract-text/)
    script_dir = Path(__file__).parent.parent
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
    print("Using Unstructured API for extraction...")
    print("-" * 50)
    
    # Extract text from each PDF
    success_count = 0
    error_count = 0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        # Extract text using API
        success, result = extract_text_from_pdf_api(pdf_file, client)
        
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
            
            # Rate limiting: wait between requests to avoid hitting API limits
            if idx < len(pdf_files):
                time.sleep(1)
                
        except Exception as e:
            print(f"  ✗ Failed to save file: {str(e)}", file=sys.stderr)
            error_count += 1
    
    # Print final summary
    print("\n" + "=" * 50)
    print(f"Summary: {success_count} successful, {error_count} failed")


if __name__ == "__main__":
    main()

