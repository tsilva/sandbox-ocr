<div align="center">
  <img src="logo.png" alt="sandbox-ocr" width="512"/>

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![uv](https://img.shields.io/badge/uv-dependency%20manager-blueviolet)](https://github.com/astral-sh/uv)

  **Convert PDFs to clean Markdown using vision-language OCR models with multi-provider support**

  [Quick Start](#quick-start) · [Providers](#providers) · [API Reference](#api-reference)
</div>

## Overview

sandbox-ocr transforms PDF documents into structured Markdown using state-of-the-art vision-language models. It handles complex layouts including equations, tables, multi-column text, and handwriting through a unified interface supporting multiple OCR providers.

## Features

- **Multi-provider support** - OLMoCR via DeepInfra, DeepSeek-OCR via vLLM or Clarifai, or any OpenAI-compatible endpoint
- **Complex document handling** - Equations, tables, multi-column layouts, handwriting recognition
- **Batch processing** - Convert multiple PDFs with colocated output alongside source files
- **Automatic completion detection** - Graceful pipeline shutdown when processing finishes
- **Configurable timeouts** - Per-PDF timeout control for large document batches

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/tsilva/sandbox-ocr.git
cd sandbox-ocr

# Install dependencies
uv sync
```

### Configuration

Create a `.env` file with your API credentials:

```bash
# OLMoCR via DeepInfra (default)
DEEPINFRA_API_KEY=your-api-key

# Optional: DeepSeek-OCR via Clarifai
CLARIFAI_PAT=your-clarifai-token

# Optional: Self-hosted vLLM
VLLM_API_KEY=optional-key
```

### Basic Usage

```python
from olmocr_extractor import convert_pdf_to_markdown

# Convert a single PDF
result = convert_pdf_to_markdown("document.pdf")

if result["success"]:
    print(result["content"])
```

### Command Line

```bash
# Convert a PDF using the default provider
uv run python olmocr_extractor.py document.pdf
```

## Providers

### OLMoCR via DeepInfra (Default)

The recommended option for most users. No GPU required.

| Property | Value |
|----------|-------|
| Endpoint | `https://api.deepinfra.com/v1/openai` |
| Model | `allenai/olmOCR-2-7B-1025` |
| Pricing | ~$0.09/1M input tokens, ~$0.19/1M output |

```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor(provider="olmocr-deepinfra")
result = extractor.convert_pdf("document.pdf")
```

### DeepSeek-OCR via vLLM (Self-hosted)

Best for high-volume processing with local GPU infrastructure.

| Property | Value |
|----------|-------|
| Endpoint | `http://localhost:8000/v1` |
| Model | `deepseek-ai/DeepSeek-OCR` |
| Speed | ~2500 tokens/second on A100-40G |

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-OCR \
    --trust-remote-code \
    --port 8000
```

```python
extractor = OLMoCRExtractor(
    provider="deepseek-vllm",
    endpoint="http://localhost:8000/v1"
)
```

### DeepSeek-OCR via Clarifai

Managed cloud hosting with no GPU setup required.

```python
extractor = OLMoCRExtractor(provider="deepseek-clarifai")
```

### Provider Comparison

| Feature | OLMoCR (DeepInfra) | DeepSeek-OCR (vLLM) | DeepSeek-OCR (Clarifai) |
|---------|-------------------|---------------------|------------------------|
| Setup | Easy | Hard | Easy |
| GPU Required | No | Yes | No |
| Speed | Fast | Very Fast | Fast |
| Cost | Pay-per-use | Hardware only | Pay-per-use |
| Best For | General use | High volume | Quick setup |

## API Reference

### OLMoCRExtractor

```python
class OLMoCRExtractor:
    def __init__(
        self,
        api_key: str = None,           # API key (or load from env)
        workspace_dir: str = "./workspace",
        endpoint: str = None,          # Override provider endpoint
        model: str = None,             # Override provider model
        provider: str = None,          # 'olmocr-deepinfra', 'deepseek-vllm', etc.
        verbose: bool = True
    )
```

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `convert_pdf()` | `pdf_path`, `timeout` | `dict` | Convert single PDF |
| `convert_pdfs()` | `pdf_paths`, `timeout` | `dict` | Convert multiple PDFs |
| `convert_pdfs_colocated()` | `pdf_paths`, `timeout_per_pdf` | `dict` | Convert with output alongside source |
| `get_markdown_content()` | `markdown_path` | `str` | Read generated markdown |
| `preview_markdown()` | `markdown_path`, `max_chars` | `str` | Preview with truncation |

### Batch Processing

Process multiple PDFs with output files placed alongside the originals:

```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor()

results = extractor.convert_pdfs_colocated(
    pdf_paths=["doc1.pdf", "reports/doc2.pdf"],
    timeout_per_pdf=300
)

print(f"Converted: {results['success_count']}/{len(results['results'])}")
```

### Convenience Function

```python
from olmocr_extractor import convert_pdf_to_markdown

result = convert_pdf_to_markdown(
    "document.pdf",
    provider="deepseek-vllm",
    endpoint="http://localhost:8000/v1"
)
```

## Project Structure

```
sandbox-ocr/
├── olmocr_extractor.py    # Main extractor class
├── ocr_providers.py       # Provider configurations
├── test_colocated.py      # Batch conversion example
├── test_deepseek.py       # DeepSeek-OCR tests
├── test_ocr.py            # Legacy test script
├── pyproject.toml         # Dependencies
└── workspace/             # Output directory (gitignored)
    └── markdown/          # Generated markdown files
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPINFRA_API_KEY` | Yes* | DeepInfra API key for OLMoCR |
| `CLARIFAI_PAT` | No | Clarifai token for DeepSeek-OCR |
| `VLLM_API_KEY` | No | Optional key for secured vLLM server |
| `CUSTOM_API_KEY` | No | API key for custom endpoints |
| `CUSTOM_OCR_ENDPOINT` | No | Custom endpoint URL |
| `CUSTOM_OCR_MODEL` | No | Custom model name |

*Required when using the default OLMoCR provider.

## References

- [OLMoCR GitHub](https://github.com/allenai/olmocr)
- [DeepInfra Model Page](https://deepinfra.com/allenai/olmOCR-2-7B-1025)
- [DeepSeek-OCR GitHub](https://github.com/deepseek-ai/DeepSeek-OCR)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Allen Institute for AI Blog](https://allenai.org/blog/olmocr-2)

## License

MIT
