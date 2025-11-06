# OLMoCR Extractor - Usage Guide

This guide shows how to use `olmocr_extractor.py` in your own projects.

## Installation

### 1. Copy the file
Copy `olmocr_extractor.py` to your project directory.

### 2. Install dependencies

Add these to your `requirements.txt`:
```
olmocr
python-dotenv  # Optional, for .env file support
```

Or if using `uv`:
```bash
uv add olmocr python-dotenv
```

Or with pip:
```bash
pip install olmocr python-dotenv
```

### 3. Get API Key
Sign up at [DeepInfra](https://deepinfra.com/) and get your API key.

## Usage Examples

### Basic Usage - Single PDF

```python
from olmocr_extractor import convert_pdf_to_markdown

# Simple one-liner conversion
result = convert_pdf_to_markdown(
    "document.pdf",
    api_key="your_deepinfra_api_key"
)

if result["success"]:
    print(f"Markdown saved to: {result['markdown_file']}")
    print(f"Content preview: {result['content'][:200]}...")
else:
    print(f"Error: {result['error']}")
```

### Using the Class - More Control

```python
from olmocr_extractor import OLMoCRExtractor

# Initialize extractor
extractor = OLMoCRExtractor(
    api_key="your_deepinfra_api_key",
    workspace_dir="./ocr_output",
    verbose=True  # Show progress
)

# Convert single PDF
result = extractor.convert_pdf("report.pdf")

if result["success"]:
    # Access the markdown file path
    md_file = result['markdown_file']

    # Access the content directly
    content = result['content']

    # Or preview it
    preview = extractor.preview_markdown(md_file, max_chars=1000)
    print(preview)
```

### Convert Multiple PDFs

```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor(api_key="your_api_key")

# Convert multiple PDFs in one go
result = extractor.convert_pdfs([
    "chapter1.pdf",
    "chapter2.pdf",
    "chapter3.pdf"
])

if result["success"]:
    # Access all generated markdown files
    for md_file in result['markdown_files']:
        print(f"Generated: {md_file}")
        content = result['contents'][md_file]
        print(f"Length: {len(content)} characters\n")
```

### Using Environment Variables

```python
import os
from olmocr_extractor import OLMoCRExtractor

# Load from .env file
from dotenv import load_dotenv
load_dotenv()

# No need to pass api_key - will read from DEEPINFRA_API_KEY env var
extractor = OLMoCRExtractor(workspace_dir="./output")

result = extractor.convert_pdf("document.pdf")
```

### With Timeout

```python
from olmocr_extractor import OLMoCRExtractor

extractor = OLMoCRExtractor(api_key="your_api_key")

# Set a timeout of 300 seconds (5 minutes)
result = extractor.convert_pdf(
    "large_document.pdf",
    timeout=300
)

if not result["success"]:
    print(f"Conversion failed or timed out: {result['error']}")
```

### Custom Model/Endpoint

```python
from olmocr_extractor import OLMoCRExtractor

# Use custom endpoint or model
extractor = OLMoCRExtractor(
    api_key="your_api_key",
    endpoint="https://custom-endpoint.com/v1/openai",
    model="custom-model-name",
    workspace_dir="./output"
)

result = extractor.convert_pdf("document.pdf")
```

## Command Line Usage

You can also run it directly from the command line:

```bash
# Make sure DEEPINFRA_API_KEY is set in environment or .env file
export DEEPINFRA_API_KEY="your_api_key"

# Run the extractor
python olmocr_extractor.py document.pdf
```

## Integration Examples

### Flask Web App

```python
from flask import Flask, request, jsonify
from olmocr_extractor import OLMoCRExtractor
import os

app = Flask(__name__)
extractor = OLMoCRExtractor(
    api_key=os.getenv("DEEPINFRA_API_KEY"),
    workspace_dir="./uploads/ocr_output"
)

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filepath = f"./uploads/{file.filename}"
    file.save(filepath)

    result = extractor.convert_pdf(filepath)

    if result["success"]:
        return jsonify({
            "success": True,
            "content": result["content"]
        })
    else:
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500
```

### Batch Processing Script

```python
from pathlib import Path
from olmocr_extractor import OLMoCRExtractor

def batch_convert_directory(input_dir, output_dir):
    """Convert all PDFs in a directory"""
    extractor = OLMoCRExtractor(workspace_dir=output_dir)

    pdf_files = list(Path(input_dir).glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        result = extractor.convert_pdf(pdf_file)

        if result["success"]:
            print(f"  ✓ Success: {result['markdown_file']}")
        else:
            print(f"  ✗ Failed: {result['error']}")

# Usage
batch_convert_directory("./pdfs", "./markdown_output")
```

## Return Value Structure

### Single PDF Conversion
```python
{
    "success": True,
    "markdown_file": "/path/to/output.md",
    "content": "# Markdown content here..."
}
```

### Multiple PDFs Conversion
```python
{
    "success": True,
    "markdown_files": ["/path/to/file1.md", "/path/to/file2.md"],
    "contents": {
        "/path/to/file1.md": "# Content 1...",
        "/path/to/file2.md": "# Content 2..."
    }
}
```

### Error Response
```python
{
    "success": False,
    "error": "Error message here"
}
```

## Tips

1. **API Key Security**: Never hardcode API keys. Use environment variables or .env files.

2. **Large Documents**: Use the `timeout` parameter for large PDFs to prevent hanging.

3. **Batch Processing**: When processing multiple PDFs, use `convert_pdfs()` instead of calling `convert_pdf()` multiple times - it's more efficient.

4. **Output Organization**: The workspace directory will contain a `markdown/` subdirectory with all generated files.

5. **Error Handling**: Always check `result["success"]` before accessing other fields.

## Cost Estimation

The allenai/olmOCR-2-7B-1025 model on DeepInfra costs approximately:
- **Input**: ~$0.09 per 1M tokens
- **Output**: ~$0.19 per 1M tokens

A typical page might use 1000-3000 tokens depending on complexity.
