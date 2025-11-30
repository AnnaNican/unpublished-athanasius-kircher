#!/usr/bin/env python3
"""
main.py
-------

Main orchestration script for the Kircher text processing pipeline.

Workflow:
1. Extract text from PDFs (extract-text/)
2. Translate Latin text to English (extract-text/)
3. Clean and format text (clean-text/)
4. Generate new text using style guide (generate-text/)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


# Script paths relative to project root
EXTRACT_PDF_TEXT = Path("extract-text/extract_pdf_text.py")
EXTRACT_PDF_API = Path("extract-text/extract_pdf_api.py")
TRANSLATE = Path("extract-text/translate-kircher.py")
FORMAT_TXT = Path("clean-text/format-txt.py")
FORMAT_TXT_EN = Path("clean-text/format_txt_en.py")
EXTRACT_STYLE = Path("generate-text/extract_style.py")
GENERATE_NOVEL = Path("generate-text/generate-novel.py")


def run_script(script_path: Path, args: list[str] | None = None) -> bool:
    """
    Run a Python script and return True if successful.
    
    Args:
        script_path: Path to the script to run
        args: Additional arguments to pass to the script
        
    Returns:
        bool: True if script exited successfully
    """
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}", file=sys.stderr)
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*60}")
    print(f"Running: {script_path.name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=False, cwd=Path(__file__).parent)
        if result.returncode != 0:
            print(f"✗ {script_path.name} failed with exit code {result.returncode}", file=sys.stderr)
            return False
        print(f"✓ {script_path.name} completed successfully")
        return True
    except Exception as e:
        print(f"✗ Error running {script_path.name}: {e}", file=sys.stderr)
        return False


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Orchestrate the Kircher text processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow stages:
  1. extract    - Extract text from PDFs
  2. translate  - Translate Latin text to English
  3. clean      - Clean and format extracted text
  4. generate   - Generate new text using style guide

Examples:
  # Run full pipeline
  python main.py --all

  # Run specific stages
  python main.py --extract --translate
  python main.py --clean --generate

  # Generate with custom word count
  python main.py --generate --words 10000 --topic "subterranean worlds"
        """
    )
    
    # Stage flags
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all stages in sequence (extract → translate → clean → generate)",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract text from PDFs (uses extract_pdf_text.py)",
    )
    parser.add_argument(
        "--extract-api",
        action="store_true",
        help="Extract text from PDFs using Unstructured API (uses extract_pdf_api.py)",
    )
    parser.add_argument(
        "--translate",
        action="store_true",
        help="Translate Latin text files to English",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean and format text files",
    )
    parser.add_argument(
        "--clean-en",
        action="store_true",
        help="Clean English text files (txt-en folder)",
    )
    parser.add_argument(
        "--extract-style",
        action="store_true",
        help="Extract style guide from translated texts",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate new text using style guide",
    )
    
    # Generation options
    parser.add_argument(
        "--words",
        type=int,
        default=50000,
        help="Target word count for generation (default: 50000)",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="",
        help="Topic/seed idea for text generation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("unpublished-kircher.md"),
        help="Output file for generated text (default: unpublished-kircher.md)",
    )
    
    return parser.parse_args()


def main() -> None:
    """Main orchestration function."""
    args = parse_args()
    
    # If --all is specified, run full pipeline
    if args.all:
        print("Running full pipeline: extract → translate → clean → extract-style → generate")
        stages = [
            ("Extract PDFs", EXTRACT_PDF_TEXT, None),
            ("Translate", TRANSLATE, None),
            ("Clean text", FORMAT_TXT, None),
            ("Clean English text", FORMAT_TXT_EN, None),
            ("Extract style", EXTRACT_STYLE, None),
            ("Generate novel", GENERATE_NOVEL, ["--words", str(args.words), "--output", str(args.output)] + (["--topic", args.topic] if args.topic else [])),
        ]
        
        for stage_name, script_path, script_args in stages:
            if not run_script(script_path, script_args):
                print(f"\nPipeline stopped at: {stage_name}")
                sys.exit(1)
        
        print("\n" + "="*60)
        print("✓ Full pipeline completed successfully!")
        return
    
    # Run individual stages based on flags
    success = True
    
    if args.extract:
        success = run_script(EXTRACT_PDF_TEXT) and success
    
    if args.extract_api:
        success = run_script(EXTRACT_PDF_API) and success
    
    if args.translate:
        success = run_script(TRANSLATE) and success
    
    if args.clean:
        success = run_script(FORMAT_TXT) and success
    
    if args.clean_en:
        success = run_script(FORMAT_TXT_EN) and success
    
    if args.extract_style:
        success = run_script(EXTRACT_STYLE) and success
    
    if args.generate:
        gen_args = ["--words", str(args.words), "--output", str(args.output)]
        if args.topic:
            gen_args.extend(["--topic", args.topic])
        success = run_script(GENERATE_NOVEL, gen_args) and success
    
    # If no stages were specified, show help
    if not any([
        args.extract, args.extract_api, args.translate, args.clean,
        args.clean_en, args.extract_style, args.generate
    ]):
        print("No stages specified. Use --all to run full pipeline or specify individual stages.")
        print("Use --help for more information.")
        sys.exit(1)
    
    if success:
        print("\n" + "="*60)
        print("✓ All specified stages completed successfully!")
    else:
        print("\n" + "="*60)
        print("✗ Some stages failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

