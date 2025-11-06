#!/usr/bin/env python3
"""
Test script for colocated PDF to Markdown conversion.
Demonstrates converting multiple PDFs with output files placed alongside the originals.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from olmocr_extractor import OLMoCRExtractor

# Load environment variables
load_dotenv()

def main():
    # Configuration
    api_key = os.getenv("DEEPINFRA_API_KEY")

    if not api_key:
        print("Error: DEEPINFRA_API_KEY not found in .env file")
        return 1

    # Example: Convert test PDFs
    # You can specify any PDFs in your filesystem
    pdf_files = [
        "./test1.pdf",
        "./test2.pdf",
        # Add more PDFs here as needed
        # "./documents/report.pdf",
        # "./data/paper.pdf",
    ]

    # Filter to only existing files
    existing_pdfs = [p for p in pdf_files if Path(p).exists()]

    if not existing_pdfs:
        print("Error: No valid PDF files found.")
        print("Please ensure test.pdf exists or modify the pdf_files list.")
        return 1

    print(f"Found {len(existing_pdfs)} PDF(s) to process")

    # Initialize extractor
    # Note: workspace_dir is not used for colocated conversion
    extractor = OLMoCRExtractor(
        api_key=api_key,
        workspace_dir="./temp_workspace",  # Used for temp storage only
        verbose=True
    )

    # Convert PDFs with colocated output
    # Each PDF will get a .md file in the same directory
    results = extractor.convert_pdfs_colocated(
        pdf_paths=existing_pdfs,
        timeout_per_pdf=300,  # 5 minutes per PDF
        cleanup_temp=True
    )

    # Display results
    print("\n" + "=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)

    if results["success"]:
        print("All conversions completed successfully!")
    else:
        print(f"Some conversions failed ({results['failed_count']} of {len(existing_pdfs)})")

    print(f"\nSuccess: {results['success_count']}")
    print(f"Failed: {results['failed_count']}")

    print("\nDetails:")
    for pdf_path, result in results["results"].items():
        print(f"\n  {Path(pdf_path).name}:")
        if result["success"]:
            print(f"    ✓ Success")
            print(f"    Output: {result['markdown_file']}")
            content_preview = result['content'][:200]
            print(f"    Preview: {content_preview}...")
        else:
            print(f"    ✗ Failed: {result['error']}")

    return 0 if results["success"] else 1

if __name__ == "__main__":
    exit(main())
