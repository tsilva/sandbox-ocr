# Quick Start Guide

Get started with PDF to Markdown conversion in 5 minutes.

## Option 1: Default Setup (OLMoCR via DeepInfra)

**1. Install dependencies:**
```bash
uv sync
```

**2. Configure API key:**
```bash
cp .env.example .env
# Edit .env and add your DEEPINFRA_API_KEY
```

**3. Convert a PDF:**
```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor()
result = extractor.convert_pdf("your_document.pdf")

if result["success"]:
    print(f"Markdown saved to: {result['markdown_file']}")
```

**Or use the command line:**
```bash
uv run python -c "from olmocr_extractor import convert_pdf_to_markdown; result = convert_pdf_to_markdown('your_document.pdf'); print(result['content'])"
```

---

## Option 2: Batch Processing

Convert multiple PDFs with output alongside originals:

```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor()

# Converts doc1.pdf -> doc1.md, doc2.pdf -> doc2.md, etc.
results = extractor.convert_pdfs_colocated([
    "doc1.pdf",
    "doc2.pdf",
    "doc3.pdf"
])

print(f"Success: {results['success_count']}/{len(results['results'])}")
```

**Or edit and run the provided script:**
```bash
# Edit test_colocated.py to list your PDFs
uv run python test_colocated.py
```

---

## Option 3: DeepSeek-OCR (Self-hosted vLLM)

**Prerequisites:** NVIDIA GPU with CUDA

**1. Install vLLM:**
```bash
pip install vllm
```

**2. Start vLLM server:**
```bash
python -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-OCR \
    --trust-remote-code \
    --port 8000
```

**3. Use DeepSeek-OCR:**
```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor(
    provider="deepseek-vllm",
    endpoint="http://localhost:8000/v1"
)

result = extractor.convert_pdf("your_document.pdf")
```

---

## Option 4: DeepSeek-OCR (Clarifai Hosted)

**1. Get Clarifai API key:**
- Sign up at [clarifai.com](https://www.clarifai.com)
- Generate a Personal Access Token (PAT)

**2. Configure:**
```bash
# Add to .env
CLARIFAI_PAT=your-pat-token
```

**3. Use Clarifai:**
```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor(provider="deepseek-clarifai")
result = extractor.convert_pdf("your_document.pdf")
```

---

## Testing Your Setup

```bash
# List available providers
uv run python ocr_providers.py

# Test default provider (OLMoCR)
uv run python test_ocr.py

# Test batch processing
uv run python test_colocated.py

# Test DeepSeek-OCR
uv run python test_deepseek.py
```

---

## Common Issues

**"API key not found"**
- Check `.env` file exists in project root
- Verify the correct environment variable is set for your provider

**"Connection refused"** (vLLM)
- Ensure vLLM server is running: `curl http://localhost:8000/health`
- Check GPU availability: `nvidia-smi`

**"Timeout"**
- Increase timeout: `extractor.convert_pdf("file.pdf", timeout=600)`
- Large PDFs may take several minutes

---

## Next Steps

- Read `DEEPSEEK_SETUP.md` for detailed DeepSeek-OCR configuration
- Check `olmocr_extractor.py` for advanced usage options
- Review provider configurations in `ocr_providers.py`

---

## Quick Reference

### Available Providers
- `olmocr-deepinfra` - OLMoCR via DeepInfra (default)
- `deepseek-vllm` - DeepSeek-OCR self-hosted
- `deepseek-clarifai` - DeepSeek-OCR via Clarifai
- `custom` - Your own endpoint

### Key Methods
```python
# Single PDF
extractor.convert_pdf("file.pdf")

# Multiple PDFs (single workspace)
extractor.convert_pdfs(["file1.pdf", "file2.pdf"])

# Multiple PDFs (colocated output)
extractor.convert_pdfs_colocated(["file1.pdf", "file2.pdf"])
```

### Environment Variables
```bash
DEEPINFRA_API_KEY=xxx    # OLMoCR via DeepInfra
CLARIFAI_PAT=xxx         # DeepSeek via Clarifai
VLLM_API_KEY=xxx         # Self-hosted vLLM (optional)
CUSTOM_API_KEY=xxx       # Custom endpoint
```

Happy converting! 🚀
