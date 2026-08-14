<div align="center">
  <img src="https://raw.githubusercontent.com/tsilva/sandbox-ocr/main/logo.png" alt="sandbox-ocr" width="512"/>

  **📄 PDF-to-Markdown OCR conversion with multiple providers 👁️**

</div>

## Overview

A PDF-to-Markdown OCR conversion project supporting multiple providers including OLMoCR via DeepInfra, DeepSeek-OCR via vLLM, and custom OpenAI-compatible endpoints. Handles equations, tables, complex layouts, handwriting, and multi-column documents.

## Features

- **Multi-provider support** - OLMoCR, DeepSeek-OCR, custom endpoints
- **Batch processing** - Convert multiple PDFs at once
- **Colocated output** - Markdown files alongside source PDFs
- **Complex layouts** - Tables, equations, multi-column support
- **OpenAI-compatible** - Works with any compatible API

## Quick Start

```bash
# Clone and setup
git clone https://github.com/tsilva/sandbox-ocr.git
cd sandbox-ocr
uv sync

# Verify the API key stored in macOS Keychain
keyenv doctor

# Convert a PDF
keyenv run -- uv run python -c "from olmocr_extractor import convert_pdf_to_markdown; convert_pdf_to_markdown('test.pdf')"
```

Private values declared in `.keyenv.toml` are injected only into commands
launched through `keyenv run -- ...`; Python reads them normally through
`os.environ`. Keep only non-secret provider settings in `.env`.

## Providers

| Provider | Endpoint | Model |
|----------|----------|-------|
| OLMoCR (default) | DeepInfra | `allenai/olmOCR-2-7B-1025` |
| DeepSeek-OCR | vLLM (self-hosted) | `deepseek-ai/DeepSeek-OCR` |
| DeepSeek-OCR | Clarifai | `deepseek-ai/DeepSeek-OCR` |
| Custom | Any OpenAI-compatible | Configurable |

## Usage

```bash
# Single PDF conversion
keyenv run -- uv run python -c "from olmocr_extractor import convert_pdf_to_markdown; convert_pdf_to_markdown('input.pdf')"

# Batch conversion
keyenv run -- uv run python test_colocated.py

# Test DeepSeek-OCR
keyenv run -- uv run python test_deepseek.py
```

## Requirements

- Python 3.x
- uv
- API key (DeepInfra, Clarifai, or custom)

## License

MIT
