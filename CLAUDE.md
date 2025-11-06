# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a test project for OLMoCR (Optical Language Model for OCR), using DeepInfra's remote inference API to convert PDF documents to markdown. The project uses the `allenai/olmOCR-2-7B-1025` model which handles equations, tables, complex layouts, handwriting, and multi-column documents.

## Environment Setup

This project uses `uv` for dependency management. Required environment variable:
- `DEEPINFRA_API_KEY`: DeepInfra API key (stored in `.env` file, see `.env.example`)

Install dependencies:
```bash
uv sync
```

## Common Commands

### Running OCR Conversion

Main test script (requires `test.pdf` in root):
```bash
uv run python test_ocr.py
```

Direct pipeline usage:
```bash
# Single PDF
uv run python -m olmocr.pipeline ./workspace \
  --server https://api.deepinfra.com/v1/openai \
  --api_key $DEEPINFRA_API_KEY \
  --model allenai/olmOCR-2-7B-1025 \
  --markdown \
  --pdfs test.pdf

# Multiple PDFs (glob pattern)
uv run python -m olmocr.pipeline ./workspace \
  --server https://api.deepinfra.com/v1/openai \
  --api_key $DEEPINFRA_API_KEY \
  --model allenai/olmOCR-2-7B-1025 \
  --markdown \
  --pdfs "documents/*.pdf"
```

## Architecture

### Core Components

- **test_ocr.py**: Wrapper script that runs the OLMoCR pipeline with monitoring and graceful shutdown. Key features:
  - Loads configuration from `.env`
  - Monitors the pipeline's stderr for completion signals
  - Automatically terminates the pipeline when conversion is complete (watches for "Queue remaining: 0" and markdown write completion)
  - Displays preview of generated markdown

- **olmocr library**: External dependency providing the OCR pipeline (`olmocr.pipeline` module)

### Processing Flow

1. `test_ocr.py` validates API key and input PDF existence
2. Spawns subprocess running `olmocr.pipeline` with DeepInfra endpoint
3. Monitors stderr logs to detect completion (queue empty + markdown written)
4. Sends SIGTERM for graceful shutdown after 3 consecutive queue-empty signals
5. Displays generated markdown files from `workspace/markdown/`

### Output Structure

All OCR output goes to `workspace/` directory:
- `workspace/markdown/`: Generated markdown files

## API Configuration

- **Endpoint**: https://api.deepinfra.com/v1/openai
- **Model**: allenai/olmOCR-2-7B-1025
- **Pricing**: ~$0.09 per 1M input tokens, ~$0.19 per 1M output tokens
