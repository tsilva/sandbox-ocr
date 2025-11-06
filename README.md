# OLMoCR Remote Inference Test

Test setup for the OLMoCR document digitization model using DeepInfra's remote inference API.

## Setup

This project uses `uv` for dependency management and the OLMoCR model hosted on DeepInfra.

### Prerequisites

- Python 3.11+
- uv package manager
- DeepInfra API key

### Installation

```bash
# Install dependencies
uv sync
```

### Configuration

Create a `.env` file in the project root:

```env
DEEPINFRA_API_KEY=your_api_key_here
```

## Usage

### Running the test script

```bash
uv run python test_ocr.py
```

This will:
1. Load your DeepInfra API key from `.env`
2. Process `test.pdf` using the `allenai/olmOCR-2-7B-1025` model
3. Generate markdown output in the `workspace/` directory

### Using OLMoCR directly

```bash
# Basic usage
uv run python -m olmocr.pipeline ./workspace \
  --server https://api.deepinfra.com/v1/openai \
  --api_key $DEEPINFRA_API_KEY \
  --model allenai/olmOCR-2-7B-1025 \
  --markdown \
  --pdfs test.pdf

# Multiple PDFs
uv run python -m olmocr.pipeline ./workspace \
  --server https://api.deepinfra.com/v1/openai \
  --api_key $DEEPINFRA_API_KEY \
  --model allenai/olmOCR-2-7B-1025 \
  --markdown \
  --pdfs "documents/*.pdf"
```

## Output

Converted markdown files are saved to `workspace/markdown/`

## Model Information

- **Model**: allenai/olmOCR-2-7B-1025
- **Provider**: DeepInfra
- **Endpoint**: https://api.deepinfra.com/v1/openai
- **Pricing**: ~$0.09 per 1M input tokens, ~$0.19 per 1M output tokens
- **Capabilities**:
  - PDF to Markdown conversion
  - Handles equations, tables, and complex layouts
  - Supports handwriting recognition
  - Multi-column document processing
  - Automatic header/footer removal

## Project Structure

```
.
├── .env                    # API credentials (gitignored)
├── test.pdf               # Test document (gitignored)
├── test_ocr.py            # Test script
├── pyproject.toml         # Project dependencies
└── workspace/             # OCR output directory (gitignored)
    └── markdown/          # Generated markdown files
```

## References

- [OLMoCR GitHub](https://github.com/allenai/olmocr)
- [DeepInfra Model Page](https://deepinfra.com/allenai/olmOCR-2-7B-1025)
- [Allen Institute for AI](https://allenai.org/blog/olmocr-2)
