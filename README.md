<p align="center">
  <img src="https://raw.githubusercontent.com/tsilva/sandbox-ocr/main/logo.png" alt="sandbox-ocr" width="512"/>
  <br />
  <!-- repo-tagline:start -->
  <strong>📄 PDF-to-Markdown OCR conversion with multiple providers 👁️</strong>
  <!-- repo-tagline:end -->
</p>

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

# Configure and verify the deepinfra access binding first (see Service access).

# Convert a PDF
uv run python -c "from olmocr_extractor import convert_pdf_to_markdown; convert_pdf_to_markdown('test.pdf')"
```

Run credential-dependent examples below inside the selected provider's native
injection command described in [Service access](#service-access). Python reads
keys from `os.environ`; keep only non-secret provider settings in `.env`.

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
uv run python -c "from olmocr_extractor import convert_pdf_to_markdown; convert_pdf_to_markdown('input.pdf')"

# Batch conversion
uv run python test_colocated.py

# Test DeepSeek-OCR
uv run python test_deepseek.py
```

## Requirements

- Python 3.x
- uv
- API key (DeepInfra, Clarifai, or custom)

## License

MIT

## Service access

`.access.toml` declares four independent profiles: `deepinfra`, `clarifai`,
`vllm` and `custom`. It contains names and descriptions, not secret values or
an automatic injector. An unauthenticated local vLLM endpoint needs no key.

No operator binding is bundled or verified. Before using a profile, configure
its binding in ignored `.access.local.toml` with mode `0600`. Follow the version-1
schema in `/Users/tsilva/.codex/access.md`; other operators need an equivalent
validated local binding. The file contains only provider metadata: Infisical
instance, project UUID, environment and narrow folder path. Do not guess a
binding or fall back when one is invalid or absent.

Use a folder containing exactly that profile's declared variable names. Verify
folder names and then nonempty credential presence without displaying values.
Do not list secret values, use root or recursive injection, import other folders,
or write keys into `.env`, shell exports, command arguments or token caches.
A metadata inventory does not provision or move credentials.

Install the Infisical CLI and authenticate with `infisical login`. Resolve the
selected binding, then replace the uppercase metadata placeholders below:

```bash
infisical run --projectId=PROJECT_UUID --env=ENVIRONMENT --path=/NARROW_FOLDER \
  --domain=https://YOUR_INFISICAL_INSTANCE --expand=false --include-imports=false \
  --silent --telemetry=false -- \
  uv run python -c "import os; assert os.environ.get('DEEPINFRA_API_KEY'); print('DeepInfra credential present')"
```

For conversion, retain the same native injection prefix and replace only the
child command after `--` with a conversion example above. Select the matching
profile and variable for another provider; never inject all provider keys at once.
