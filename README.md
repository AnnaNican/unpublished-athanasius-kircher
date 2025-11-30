# unpublished-athanasius-kircher
project to generate a book in the style of Athanasius Kircher (for NaNoGenMo 2025)

## On Athanasius Kirker
A couple of years ago, I fell under the spell of Athanasius Kircher—a 17th-century Jesuit polymath who wrote with scientific authority about nearly everything, and was magnificently wrong about almost all of it. His encyclopedic works teetered between the fantastic and the real, baroque monuments to misguided genius. He decoded Egyptian hieroglyphs incorrectly. He mapped Atlantis with conviction. He designed impossible machines and documented creatures that never existed. I'm not alone in this obsession. Jules Verne mined his works for inspiration. Borges collected him. Umberto Eco devoted essays to his peculiar vision.
What captivates me is how Kircher's "science" reads more like speculative fiction than fact—a kind of proto-science fiction written before the genre existed. His books are fever dreams masquerading as scholarship, imagination disguised as empiricism.

While thousands of writers spend November racing to complete a novel for ~[NaNoWriMo](https://en.wikipedia.org/wiki/National_Novel_Writing_Month)~, a smaller cadre dedicates the month to writing *code* that generates novels—~[NaNoGenMo](https://nanogenmo.github.io/)~ (National Novel Generation Month). The challenge: write a program that produces a 50,000-word novel. This is my NaNoGenMo entry for 2025: a computational homage to history's most imaginative pseudoscientist.

## Project Structure

The codebase is organized into three main directories:

- **`extract-text/`** - PDF extraction and translation scripts
  - `extract_pdf_text.py` - Extract text from PDFs using PyMuPDF
  - `extract_pdf_api.py` - Extract text from PDFs using Unstructured API
  - `translate-kircher.py` - Translate Latin text to English

- **`clean-text/`** - Text cleaning and formatting scripts
  - `format-txt.py` - Clean and format extracted text files
  - `format_txt_en.py` - Clean and format English translated text files

- **`generate-text/`** - Text generation scripts
  - `extract_style.py` - Extract style guide from translated texts
  - `generate-novel.py` - Generate new text using the style guide

## Workflow Stages

The project follows a four-stage pipeline:

1. **extract** - Extract text from PDFs
   - Processes PDFs from `knowledge/pdf/` folder
   - Saves extracted text to `knowledge/txt/` folder
   - Supports both PyMuPDF and Unstructured API extraction methods

2. **translate** - Translate Latin text to English
   - Translates files from `knowledge/txt/` to `knowledge/txt-en/`
   - Uses Google Translate API via deep-translator
   - Handles chunking for large files

3. **clean** - Clean and format extracted text
   - Removes OCR artifacts, page numbers, and formatting issues
   - Normalizes whitespace and paragraph structure
   - Cleans both original and translated text files

4. **generate** - Generate new text using style guide
   - Extracts style patterns from translated texts
   - Generates new prose in Kircher's style
   - Supports large word counts (50,000+ words) with chunked generation

## Usage

The main orchestrator script (`main.py`) runs the entire pipeline:

### Run Full Pipeline

```bash
python main.py --all
```

This executes all stages in sequence: extract → translate → clean → extract-style → generate

### Run Specific Stages

```bash
# Extract PDFs and translate
python main.py --extract --translate

# Clean text files
python main.py --clean --clean-en

# Extract style guide and generate
python main.py --extract-style --generate
```

### Generate with Custom Parameters

```bash
# Generate with custom word count and topic
python main.py --generate --words 10000 --topic "subterranean worlds"

# Use Unstructured API for extraction
python main.py --extract-api --translate
```

### Individual Stage Options

- `--extract` - Extract using PyMuPDF
- `--extract-api` - Extract using Unstructured API
- `--translate` - Translate Latin to English
- `--clean` - Clean original text files
- `--clean-en` - Clean English translated files
- `--extract-style` - Extract style guide from texts
- `--generate` - Generate new text
  - `--words N` - Target word count (default: 50000)
  - `--topic "text"` - Topic/seed idea for generation
  - `--output path` - Output file path (default: unpublished-kircher.md)

## Approaches

#### Approach 1: Style Extraction + Generation
- Extract style patterns from Kircher's works
- Use style guide to generate new text via Claude API

#### Approach 2: Embeddings
- [Future work]

#### Approach 3: Fine-tuning
- [Future work]




### acknowldgement 
I want to call out that this project would not be possible without the incredible work of Internet Archive that makes vast collections of books freely accessible in digital formats. Their commitment to preserving and democratizing knowledge allowed me to obtain all the necessary materials in PDF format, enabling this project. I'm deeply grateful for their mission to provide universal access to information.
