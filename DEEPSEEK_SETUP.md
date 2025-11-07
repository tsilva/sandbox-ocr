# DeepSeek-OCR Setup Guide

This guide explains how to use DeepSeek-OCR with the OLMoCRExtractor, providing three different deployment options.

## Overview

DeepSeek-OCR is a powerful OCR model that can extract structured text, formulas, and tables from complex documents. It can process up to 200K pages per day on a single A100 GPU and achieves ~2500 tokens/second inference speed.

The extractor now supports multiple OCR providers through a unified interface:
- **OLMoCR** via DeepInfra (default)
- **DeepSeek-OCR** via self-hosted vLLM
- **DeepSeek-OCR** via Clarifai
- **Custom** OpenAI-compatible endpoints

## Option 1: Self-hosted vLLM (Best for High Volume)

### Requirements
- NVIDIA GPU (A100-40G recommended for optimal performance)
- CUDA-compatible environment
- Python 3.8+

### Installation

1. Install vLLM:
```bash
pip install vllm
```

2. Start the vLLM server:
```bash
python -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-OCR \
    --trust-remote-code \
    --served-model-name deepseek-ai/DeepSeek-OCR \
    --port 8000
```

The server will download the model weights (first run only) and start serving on `http://localhost:8000`.

### Configuration

Add to your `.env` file:
```bash
# Optional: Add API key if your vLLM server requires authentication
VLLM_API_KEY=your-optional-key
```

### Usage

```python
from olmocr_extractor import OLMoCRExtractor

# Initialize with vLLM provider
extractor = OLMoCRExtractor(
    provider="deepseek-vllm",
    endpoint="http://localhost:8000/v1",  # Default vLLM endpoint
    verbose=True
)

# Convert PDF to markdown
result = extractor.convert_pdf("document.pdf")

if result["success"]:
    print(f"Markdown saved to: {result['markdown_file']}")
    print(result['content'])
```

### Performance
- **Speed**: ~2500 tokens/second on A100-40G
- **Throughput**: Up to 200K pages/day on single GPU
- **Cost**: Free (hardware costs only)

---

## Option 2: Clarifai Hosted API (Easiest Setup)

### Setup

1. Sign up at [clarifai.com](https://www.clarifai.com)
2. Generate a Personal Access Token (PAT)
3. Add to your `.env` file:
```bash
CLARIFAI_PAT=your-clarifai-pat-token
```

### Usage

```python
from olmocr_extractor import OLMoCRExtractor

# Initialize with Clarifai provider
extractor = OLMoCRExtractor(
    provider="deepseek-clarifai",
    verbose=True
)

# Convert PDF to markdown
result = extractor.convert_pdf("document.pdf")
```

### Benefits
- No GPU required
- No model hosting
- OpenAI-compatible API
- Quick setup

### Note
Check Clarifai's current pricing and rate limits at their website.

---

## Option 3: Custom OpenAI-Compatible Endpoint

Use any OpenAI-compatible OCR service.

### Configuration

Add to your `.env` file:
```bash
CUSTOM_API_KEY=your-api-key
CUSTOM_OCR_ENDPOINT=https://your-endpoint.com/v1
CUSTOM_OCR_MODEL=your-model-name
```

### Usage

```python
from olmocr_extractor import OLMoCRExtractor

# Initialize with custom endpoint
extractor = OLMoCRExtractor(
    api_key=os.getenv("CUSTOM_API_KEY"),
    endpoint=os.getenv("CUSTOM_OCR_ENDPOINT"),
    model=os.getenv("CUSTOM_OCR_MODEL"),
    verbose=True
)

result = extractor.convert_pdf("document.pdf")
```

---

## Batch Processing with Colocated Output

Process multiple PDFs with output files alongside originals:

```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor(provider="deepseek-vllm")

# Convert multiple PDFs
# Markdown files will be created in same directory as PDFs
results = extractor.convert_pdfs_colocated(
    pdf_paths=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    timeout_per_pdf=300,  # 5 minutes per PDF
    cleanup_temp=True
)

# Check results
print(f"Success: {results['success_count']}/{len(results['results'])}")
for pdf_path, result in results['results'].items():
    if result['success']:
        print(f"✓ {pdf_path} -> {result['markdown_file']}")
    else:
        print(f"✗ {pdf_path}: {result['error']}")
```

---

## Comparing Providers

| Feature | OLMoCR (DeepInfra) | DeepSeek-OCR (vLLM) | DeepSeek-OCR (Clarifai) |
|---------|-------------------|---------------------|------------------------|
| Setup Difficulty | Easy | Hard | Easy |
| GPU Required | No | Yes | No |
| Speed | Fast | Very Fast (~2500 tok/s) | Fast |
| Cost | Pay-per-use (~$0.09-0.19/1M tokens) | Hardware only | Pay-per-use |
| Best For | General use, testing | High volume, local processing | Quick setup, cloud |

---

## Testing Your Setup

Run the test script to verify your configuration:

```bash
# Show available providers
uv run python ocr_providers.py

# Test DeepSeek-OCR configurations
uv run python test_deepseek.py
```

---

## Troubleshooting

### vLLM Server Won't Start
- Check GPU availability: `nvidia-smi`
- Ensure CUDA is properly installed
- Verify sufficient GPU memory (24GB+ recommended)

### Connection Refused
- Ensure vLLM server is running: `curl http://localhost:8000/health`
- Check firewall settings
- Verify port 8000 is not in use

### Out of Memory
- Reduce batch size in vLLM config
- Use smaller model variant if available
- Consider using Clarifai hosted option instead

### API Key Errors
- Verify `.env` file is in the correct directory
- Check environment variable names match provider requirements
- Ensure API key has proper permissions

---

## Advanced Configuration

### Custom vLLM Port

```python
extractor = OLMoCRExtractor(
    provider="deepseek-vllm",
    endpoint="http://localhost:9000/v1",  # Custom port
)
```

### Disable Verbose Output

```python
extractor = OLMoCRExtractor(
    provider="deepseek-vllm",
    verbose=False  # Suppress progress messages
)
```

### Custom Timeout

```python
result = extractor.convert_pdf(
    "large_document.pdf",
    timeout=600  # 10 minutes
)
```

---

## Resources

- **DeepSeek-OCR GitHub**: https://github.com/deepseek-ai/DeepSeek-OCR
- **vLLM Documentation**: https://docs.vllm.ai/
- **Clarifai Platform**: https://www.clarifai.com
- **Model on Hugging Face**: https://huggingface.co/deepseek-ai/DeepSeek-OCR

---

## Next Steps

1. Choose your deployment option (vLLM, Clarifai, or custom)
2. Set up environment variables in `.env`
3. Run `test_deepseek.py` to verify setup
4. Start converting PDFs to markdown!

For questions or issues, refer to the DeepSeek-OCR repository or open an issue in this project.
