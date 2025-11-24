#!/usr/bin/env python3
"""
Translate Latin text files from knowledge/txt to English and save to knowledge/txt-en.
For non-Latin files, detect and print the language.
"""

import sys
import re
from pathlib import Path
from langdetect import detect, detect_langs, LangDetectException
from deep_translator import GoogleTranslator


def detect_language(text_sample):
    """
    Detect the language of a text sample.
    
    Args:
        text_sample: Sample text to analyze
        
    Returns:
        tuple: (primary_language_code: str, confidence: float, all_detections: list)
    """
    try:
        # Get all possible languages with confidence scores
        languages = detect_langs(text_sample)
        primary = languages[0]
        return primary.lang, primary.prob, languages
    except LangDetectException as e:
        return None, 0.0, []


def translate_text(text, source_lang='la', target_lang='en'):
    """
    Translate text from source language to target language.
    
    Args:
        text: Text to translate
        source_lang: Source language code (default: 'la' for Latin)
        target_lang: Target language code (default: 'en' for English)
        
    Returns:
        str: Translated text
    """
    try:
        # Use Google Translator through deep-translator
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        # Split text into chunks (keep under 4000 chars for safety margin)
        max_chunk_size = 4000  # characters per chunk (5000 limit with margin)
        
        # Simple case: text fits in one chunk
        if len(text) <= max_chunk_size:
            return translator.translate(text)
        
        # Split text into chunks by splitting at reasonable boundaries
        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_len = len(line) + 1  # +1 for newline
            
            # If this line alone exceeds limit, split it by words
            if line_len > max_chunk_size:
                # First, translate current chunk if any
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    if len(chunk_text) > 0:
                        chunks.append(translator.translate(chunk_text))
                    current_chunk = []
                    current_size = 0
                
                # Split long line into word chunks
                words = line.split()
                word_chunk = []
                word_size = 0
                
                for word in words:
                    word_len = len(word) + 1  # +1 for space
                    if word_size + word_len > max_chunk_size and word_chunk:
                        # Translate word chunk
                        word_text = ' '.join(word_chunk)
                        chunks.append(translator.translate(word_text))
                        word_chunk = [word]
                        word_size = word_len
                    else:
                        word_chunk.append(word)
                        word_size += word_len
                
                # Add remaining words as new chunk start
                if word_chunk:
                    current_chunk = [' '.join(word_chunk)]
                    current_size = len(current_chunk[0])
            elif current_size + line_len > max_chunk_size:
                # Current chunk is full, translate it
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    chunks.append(translator.translate(chunk_text))
                current_chunk = [line]
                current_size = line_len
            else:
                # Add line to current chunk
                current_chunk.append(line)
                current_size += line_len
        
        # Translate remaining chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if len(chunk_text) > 0:
                chunks.append(translator.translate(chunk_text))
        
        return '\n\n'.join(chunks)
    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")


def check_if_latin(text_sample):
    """
    Check if text is likely Latin by looking for Latin-specific patterns.
    
    Args:
        text_sample: Text sample to analyze
        
    Returns:
        float: Confidence score (0.0 to 1.0) that text is Latin
    """
    text_lower = text_sample.lower()
    words = text_lower.split()
    
    if len(words) < 10:
        return 0.0
    
    # Common Latin words
    latin_words = ['et', 'est', 'in', 'non', 'ad', 'per', 'de', 'pro', 'cum', 
                   'aut', 'vel', 'si', 'quod', 'quae', 'quorum', 'quibus',
                   'quid', 'quis', 'quo', 'ubi', 'unde', 'unde', 'hic', 'haec',
                   'hoc', 'ille', 'illa', 'illud', 'suus', 'sua', 'suum',
                   'tamen', 'tam', 'tunc', 'tum', 'nisi', 'igitur', 'itaque']
    
    # Common Latin endings
    latin_endings = ['us', 'um', 'ae', 'is', 'ibus', 'em', 'es', 'ibus', 
                     'orum', 'arum', 'orum', 'ibus']
    
    latin_word_count = 0
    latin_ending_count = 0
    total_words_checked = min(200, len(words))  # Check more words for better accuracy
    
    valid_words = 0
    for word in words[:total_words_checked]:
        # Remove punctuation for checking
        clean_word = word.strip('.,;:!?()[]{}"\'')
        if len(clean_word) < 2:
            continue
        
        valid_words += 1
            
        # Check for Latin words
        if clean_word in latin_words:
            latin_word_count += 1
        
        # Check for Latin endings (words ending in common Latin patterns)
        for ending in latin_endings:
            if clean_word.endswith(ending) and len(clean_word) > len(ending) + 1:
                latin_ending_count += 1
                break
    
    if valid_words == 0:
        return 0.0
    
    # Calculate confidence based on Latin word/ending frequency
    # More lenient scoring
    word_ratio = latin_word_count / valid_words
    ending_ratio = latin_ending_count / valid_words
    word_confidence = min(1.0, word_ratio * 15)  # More generous multiplier
    ending_confidence = min(1.0, ending_ratio * 5)
    
    # Also check for common Latin phrases (including historical forms)
    latin_phrases = ['et cetera', 'ad hoc', 'per se', 'pro bono', 'quid pro quo',
                     'status quo', 'in situ', 'in vitro', 'ex libris', 'de rebus',
                     'ante diluvium', 'post diluvium', 'societatis', 'jesu',
                     'apud', 'anno', 'cum privilegiis']
    phrase_count = sum(1 for phrase in latin_phrases if phrase in text_lower)
    phrase_confidence = min(1.0, phrase_count * 0.4)
    
    # Check for common Latin word patterns (like "quod", "quae", "quorum", etc.)
    latin_patterns = ['quod', 'quae', 'quorum', 'quibus', 'qui', 'qua', 'quo']
    pattern_count = sum(1 for pattern in latin_patterns if pattern in text_lower)
    pattern_confidence = min(1.0, pattern_count * 0.2)
    
    # Combined confidence (weighted average)
    confidence = (word_confidence * 0.4 + ending_confidence * 0.3 + phrase_confidence * 0.2 + pattern_confidence * 0.1)
    return min(1.0, confidence)


def get_text_sample(text, sample_size=10000):
    """
    Get a sample of text for language detection (first N characters).
    
    Args:
        text: Full text
        sample_size: Number of characters to sample
        
    Returns:
        str: Text sample
    """
    # Remove page markers for better detection
    sample = text[:sample_size]
    # Remove common page separators
    sample = sample.replace('--- Page', '')
    # Return cleaned sample
    return sample.strip()


def main():
    # Get the knowledge folder paths
    script_dir = Path(__file__).parent
    knowledge_dir = script_dir / "knowledge"
    txt_dir = knowledge_dir / "txt"
    txt_en_dir = knowledge_dir / "txt-en"
    
    if not knowledge_dir.exists():
        print(f"Error: Knowledge folder not found at {knowledge_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not txt_dir.exists():
        print(f"Error: Text folder not found at {txt_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Create txt-en directory if it doesn't exist
    txt_en_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all text files
    txt_files = sorted(list(txt_dir.glob("*.txt")) + list(txt_dir.glob("*.TXT")))
    
    if not txt_files:
        print(f"No text files found in {txt_dir}")
        return
    
    print(f"Found {len(txt_files)} text file(s) in knowledge/txt folder")
    print("-" * 50)
    
    latin_count = 0
    translated_count = 0
    error_count = 0
    language_map = {}
    
    # Process each text file
    for txt_file in txt_files:
        print(f"\nProcessing: {txt_file.name}")
        
        try:
            # Read the text file
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()
            
            if not text.strip():
                print(f"  ⚠ Warning: File is empty")
                continue
            
            # Get a sample for language detection
            text_sample = get_text_sample(text)
            
            # Detect language
            lang_code, confidence, all_langs = detect_language(text_sample)
            
            if lang_code is None:
                print(f"  ✗ Could not detect language")
                error_count += 1
                continue
            
            # Map language codes to names
            lang_names = {
                'la': 'Latin',
                'en': 'English',
                'fr': 'French',
                'de': 'German',
                'es': 'Spanish',
                'it': 'Italian',
                'pt': 'Portuguese',
                'nl': 'Dutch',
                'pl': 'Polish',
                'ru': 'Russian',
                'ca': 'Catalan',
                'ro': 'Romanian',
            }
            lang_name = lang_names.get(lang_code, lang_code.upper())
            
            # Check if it might be Latin
            is_latin = False
            latin_confidence_score = 0.0
            
            # First check: directly detected as Latin
            if lang_code == 'la':
                is_latin = True
                print(f"  Language detected: Latin (confidence: {confidence:.2%})")
            else:
                # Second check: if detected as Romance language, verify with Latin pattern matching
                # Historical Latin texts are often misclassified as Romance languages
                romance_langs = ['ca', 'it', 'ro', 'es', 'pt', 'fr']
                if lang_code in romance_langs:
                    latin_confidence_score = check_if_latin(text_sample)
                    # Lower threshold to catch more Latin texts
                    if latin_confidence_score > 0.2:  # More aggressive threshold
                        is_latin = True
                        print(f"  Language detected: {lang_name} (confidence: {confidence:.2%})")
                        print(f"  ⚠ Reclassified as Latin based on pattern analysis (Latin confidence: {latin_confidence_score:.2%})")
                        lang_name = 'Latin'
                    else:
                        print(f"  Language detected: {lang_name} (confidence: {confidence:.2%})")
                        print(f"  ℹ Latin pattern check: {latin_confidence_score:.2%} (below threshold)")
                else:
                    print(f"  Language detected: {lang_name} (confidence: {confidence:.2%})")
            
            # Track language statistics (track original detection for non-Latin, Latin for Latin)
            track_lang = 'Latin' if is_latin else lang_name
            if track_lang not in language_map:
                language_map[track_lang] = 0
            language_map[track_lang] += 1
            
            # If Latin (or detected as likely Latin), translate to English
            if is_latin:
                latin_count += 1
                print(f"  → Translating from Latin to English...")
                
                try:
                    translated_text = translate_text(text, source_lang='la', target_lang='en')
                    
                    # Save translated text
                    output_file = txt_en_dir / f"{txt_file.stem}.txt"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(translated_text)
                    
                    translated_count += 1
                    word_count = len(translated_text.split())
                    char_count = len(translated_text)
                    print(f"  ✓ Translated and saved: {word_count:,} words ({char_count:,} characters)")
                    print(f"  ✓ Saved to: {output_file.name}")
                except Exception as e:
                    print(f"  ✗ Translation failed: {str(e)}")
                    error_count += 1
            else:
                print(f"  ℹ Not Latin - no translation performed")
                # Show top language candidates
                if len(all_langs) > 1:
                    print(f"  Top candidates:")
                    for lang_result in all_langs[:3]:
                        candidate_name = lang_names.get(lang_result.lang, lang_result.lang.upper())
                        print(f"    - {candidate_name}: {lang_result.prob:.2%}")
        
        except Exception as e:
            print(f"  ✗ Error processing file: {str(e)}")
            error_count += 1
    
    # Print final summary
    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  - Latin files found: {latin_count}")
    print(f"  - Successfully translated: {translated_count}")
    print(f"  - Errors: {error_count}")
    print(f"\nLanguage distribution:")
    for lang_name, count in sorted(language_map.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {lang_name}: {count} file(s)")


if __name__ == "__main__":
    main()

