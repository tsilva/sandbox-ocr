# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PDF-to-Markdown OCR conversion project supporting multiple OCR providers:
- **OLMoCR** via DeepInfra (default) - `allenai/olmOCR-2-7B-1025`
- **DeepSeek-OCR** via self-hosted vLLM - `deepseek-ai/DeepSeek-OCR`
- **DeepSeek-OCR** via Clarifai
- **Custom** OpenAI-compatible endpoints

All providers use OpenAI-compatible API format and handle equations, tables, complex layouts, handwriting, and multi-column documents.

## Environment Setup

This project uses `uv` for dependency management. Environment variables (stored in `.env` file, see `.env.example`):
- `DEEPINFRA_API_KEY`: DeepInfra API key (for OLMoCR)
- `CLARIFAI_PAT`: Clarifai Personal Access Token (for DeepSeek-OCR via Clarifai)
- `VLLM_API_KEY`: Optional key for secured vLLM server (for self-hosted DeepSeek-OCR)
- `CUSTOM_API_KEY`, `CUSTOM_OCR_ENDPOINT`, `CUSTOM_OCR_MODEL`: For custom endpoints

Install dependencies:
```bash
uv sync
```

## Common Commands

### Running OCR Conversion

**Using OLMoCRExtractor (Recommended)**:
```bash
# Single PDF with default provider (OLMoCR via DeepInfra)
uv run python -c "from olmocr_extractor import convert_pdf_to_markdown; convert_pdf_to_markdown('test.pdf')"

# Multiple PDFs with colocated output
uv run python test_colocated.py

# Using DeepSeek-OCR via vLLM
uv run python test_deepseek.py
```

**Legacy test script** (requires `test.pdf` in root):
```bash
uv run python test_ocr.py
```

**Direct pipeline usage** (low-level):
```bash
# Single PDF
uv run python -m olmocr.pipeline ./workspace \
  --server https://api.deepinfra.com/v1/openai \
  --api_key $DEEPINFRA_API_KEY \
  --model allenai/olmOCR-2-7B-1025 \
  --markdown \
  --pdfs test.pdf
```

### Provider Management

```bash
# List available OCR providers
uv run python ocr_providers.py

# Test DeepSeek-OCR configurations
uv run python test_deepseek.py
```

## Architecture

### Core Components

- **olmocr_extractor.py**: Main OCR extraction class supporting multiple providers. Key features:
  - Multi-provider support (OLMoCR, DeepSeek-OCR, custom endpoints)
  - Single and batch PDF conversion
  - Colocated output (markdown files alongside PDFs)
  - Automatic completion detection and graceful shutdown
  - Configurable timeouts and verbose logging

- **ocr_providers.py**: Provider configuration system defining endpoints, models, and API keys for various OCR services

- **test_colocated.py**: Batch conversion script that processes multiple PDFs with output alongside originals

- **test_deepseek.py**: Testing suite for DeepSeek-OCR configurations (vLLM, Clarifai, custom endpoints)

- **test_ocr.py**: Legacy wrapper script for single PDF conversion (kept for backward compatibility)

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

## Provider Configurations

### Default: OLMoCR via DeepInfra
- **Endpoint**: https://api.deepinfra.com/v1/openai
- **Model**: allenai/olmOCR-2-7B-1025
- **Pricing**: ~$0.09 per 1M input tokens, ~$0.19 per 1M output tokens
- **Setup**: Set `DEEPINFRA_API_KEY` in `.env`

### DeepSeek-OCR via vLLM (Self-hosted)
- **Endpoint**: http://localhost:8000/v1 (configurable)
- **Model**: deepseek-ai/DeepSeek-OCR
- **Performance**: ~2500 tokens/second on A100-40G
- **Setup**: See `DEEPSEEK_SETUP.md` for complete installation guide

### DeepSeek-OCR via Clarifai
- **Endpoint**: Clarifai's OpenAI-compatible endpoint
- **Model**: deepseek-ai/DeepSeek-OCR
- **Setup**: Set `CLARIFAI_PAT` in `.env`

For detailed DeepSeek-OCR setup instructions, see **DEEPSEEK_SETUP.md**.
