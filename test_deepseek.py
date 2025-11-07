#!/usr/bin/env python3
"""
DeepSeek-OCR Test Script
=========================

Example usage of DeepSeek-OCR with the OLMoCRExtractor.

Setup Options:

1. Self-hosted vLLM (Requires GPU):
   ```bash
   # Install vLLM
   pip install vllm

   # Start vLLM server
   python -m vllm.entrypoints.openai.api_server \
       --model deepseek-ai/DeepSeek-OCR \
       --trust-remote-code \
       --served-model-name deepseek-ai/DeepSeek-OCR \
       --port 8000
   ```

2. Clarifai Hosted:
   - Sign up at clarifai.com
   - Get your Personal Access Token (PAT)
   - Set CLARIFAI_PAT environment variable

3. Other OpenAI-compatible endpoints:
   - Specify custom endpoint and model
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from olmocr_extractor import OLMoCRExtractor
from ocr_providers import print_providers

# Load environment variables
load_dotenv()


def test_deepseek_vllm():
    """Test DeepSeek-OCR via self-hosted vLLM."""
    print("\n" + "=" * 80)
    print("Testing DeepSeek-OCR via Self-hosted vLLM")
    print("=" * 80)

    # Check if vLLM server is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()

    if result != 0:
        print("\nError: vLLM server not running on localhost:8000")
        print("Please start the vLLM server first. See script header for instructions.")
        return None

    extractor = OLMoCRExtractor(
        provider="deepseek-vllm",
        endpoint="http://localhost:8000/v1",
        verbose=True
    )

    # Convert test PDF
    pdf_file = "./test1.pdf"
    if not Path(pdf_file).exists():
        print(f"\nError: {pdf_file} not found")
        return None

    result = extractor.convert_pdf(pdf_file)

    if result["success"]:
        print(f"\n✓ Success! Output: {result['markdown_file']}")
        print(f"Preview: {result['content'][:200]}...")
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")

    return result


def test_deepseek_clarifai():
    """Test DeepSeek-OCR via Clarifai."""
    print("\n" + "=" * 80)
    print("Testing DeepSeek-OCR via Clarifai")
    print("=" * 80)

    api_key = os.getenv("CLARIFAI_PAT")
    if not api_key:
        print("\nError: CLARIFAI_PAT not found in environment")
        print("Please set CLARIFAI_PAT environment variable")
        return None

    extractor = OLMoCRExtractor(
        provider="deepseek-clarifai",
        api_key=api_key,
        verbose=True
    )

    # Convert test PDF
    pdf_file = "./test1.pdf"
    if not Path(pdf_file).exists():
        print(f"\nError: {pdf_file} not found")
        return None

    result = extractor.convert_pdf(pdf_file)

    if result["success"]:
        print(f"\n✓ Success! Output: {result['markdown_file']}")
        print(f"Preview: {result['content'][:200]}...")
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")

    return result


def test_custom_endpoint():
    """Test with custom OpenAI-compatible endpoint."""
    print("\n" + "=" * 80)
    print("Testing Custom Endpoint")
    print("=" * 80)

    # Example: Use any OpenAI-compatible endpoint
    custom_endpoint = os.getenv("CUSTOM_OCR_ENDPOINT")
    custom_model = os.getenv("CUSTOM_OCR_MODEL")
    custom_key = os.getenv("CUSTOM_API_KEY")

    if not all([custom_endpoint, custom_model, custom_key]):
        print("\nSkipping: Custom endpoint not configured")
        print("Set CUSTOM_OCR_ENDPOINT, CUSTOM_OCR_MODEL, and CUSTOM_API_KEY to test")
        return None

    extractor = OLMoCRExtractor(
        api_key=custom_key,
        endpoint=custom_endpoint,
        model=custom_model,
        verbose=True
    )

    # Convert test PDF
    pdf_file = "./test1.pdf"
    if not Path(pdf_file).exists():
        print(f"\nError: {pdf_file} not found")
        return None

    result = extractor.convert_pdf(pdf_file)

    if result["success"]:
        print(f"\n✓ Success! Output: {result['markdown_file']}")
        print(f"Preview: {result['content'][:200]}...")
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")

    return result


def main():
    print("=" * 80)
    print("DeepSeek-OCR Testing Suite")
    print("=" * 80)

    # Show available providers
    print("\nAvailable Providers:")
    print_providers()

    # Test each provider
    print("\n" + "=" * 80)
    print("Running Tests")
    print("=" * 80)

    results = {}

    # Test 1: Self-hosted vLLM
    result = test_deepseek_vllm()
    results["vllm"] = result

    # Test 2: Clarifai
    result = test_deepseek_clarifai()
    results["clarifai"] = result

    # Test 3: Custom endpoint
    result = test_custom_endpoint()
    results["custom"] = result

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    for name, result in results.items():
        if result is None:
            print(f"  {name}: SKIPPED")
        elif result.get("success"):
            print(f"  {name}: ✓ PASSED")
        else:
            print(f"  {name}: ✗ FAILED")

    return 0


if __name__ == "__main__":
    exit(main())
