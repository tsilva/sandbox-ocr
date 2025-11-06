#!/usr/bin/env python3
"""Debug test for colocated conversion."""

import os
from pathlib import Path
from dotenv import load_dotenv
from olmocr_extractor import OLMoCRExtractor

load_dotenv()

def main():
    api_key = os.getenv("DEEPINFRA_API_KEY")
    if not api_key:
        print("Error: DEEPINFRA_API_KEY not found")
        return 1

    extractor = OLMoCRExtractor(
        api_key=api_key,
        workspace_dir="./temp_workspace",
        verbose=True
    )

    # Test with just one PDF and no cleanup
    results = extractor.convert_pdfs_colocated(
        pdf_paths=["./test1.pdf"],
        timeout_per_pdf=300,
        cleanup_temp=False  # Don't cleanup so we can inspect
    )

    print("\n" + "=" * 80)
    print("DEBUG INFO")
    print("=" * 80)

    for pdf_path, result in results["results"].items():
        print(f"\nPDF: {pdf_path}")
        print(f"Success: {result['success']}")
        if not result["success"]:
            print(f"Error: {result.get('error', 'Unknown')}")

    # List temp directories
    import tempfile
    temp_dir = Path(tempfile.gettempdir())
    olmocr_temps = list(temp_dir.glob("olmocr_*"))
    print(f"\nTemp directories found: {len(olmocr_temps)}")
    for temp in olmocr_temps:
        print(f"\n  {temp}:")
        for item in temp.rglob("*"):
            if item.is_file():
                print(f"    - {item.relative_to(temp)} ({item.stat().st_size} bytes)")

    return 0

if __name__ == "__main__":
    exit(main())
