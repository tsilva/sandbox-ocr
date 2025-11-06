#!/usr/bin/env python3
"""
Test script for OLMoCR with DeepInfra remote inference.
Converts test.pdf to markdown using the allenai/olmOCR-2-7B-1025 model.
"""

import os
import subprocess
import signal
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
DEEPINFRA_ENDPOINT = "https://api.deepinfra.com/v1/openai"
MODEL_NAME = "allenai/olmOCR-2-7B-1025"
WORKSPACE_DIR = "./workspace"
TEST_PDF = "./test.pdf"

def main():
    # Validate configuration
    if not DEEPINFRA_API_KEY:
        print("Error: DEEPINFRA_API_KEY not found in .env file")
        return 1

    if not Path(TEST_PDF).exists():
        print(f"Error: Test PDF not found at {TEST_PDF}")
        return 1

    print("=" * 80)
    print("OLMoCR Remote Inference Test")
    print("=" * 80)
    print(f"Endpoint: {DEEPINFRA_ENDPOINT}")
    print(f"Model: {MODEL_NAME}")
    print(f"Input: {TEST_PDF}")
    print(f"Output: {WORKSPACE_DIR}/")
    print("=" * 80)
    print()

    # Build the command
    cmd = [
        "python", "-m", "olmocr.pipeline",
        WORKSPACE_DIR,
        "--server", DEEPINFRA_ENDPOINT,
        "--api_key", DEEPINFRA_API_KEY,
        "--model", MODEL_NAME,
        "--markdown",
        "--pdfs", TEST_PDF,
    ]

    print("Running OCR conversion...")
    print()

    # Run the command with monitoring
    try:
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Monitor stderr for completion signals
        queue_empty_count = 0
        markdown_written = False

        for line in iter(process.stderr.readline, ''):
            # Show important log lines
            if any(keyword in line for keyword in ['INFO', 'ERROR', 'WARNING', 'Queue remaining', 'Writing', 'markdown']):
                print(line.rstrip())

            # Track completion signals
            if 'Writing' in line and 'markdown' in line:
                markdown_written = True

            if 'Queue remaining: 0' in line and markdown_written:
                queue_empty_count += 1
                # After seeing queue empty 3 times, we're definitely done
                if queue_empty_count >= 3:
                    print("\n✓ Processing complete, shutting down pipeline...")
                    time.sleep(0.5)  # Brief grace period
                    process.send_signal(signal.SIGTERM)
                    process.wait(timeout=5)
                    break

        # Check if process exited normally
        if process.poll() is None:
            # Still running, force terminate
            process.terminate()
            process.wait(timeout=5)

        print()
        print("=" * 80)
        print("Conversion completed successfully!")
        print("=" * 80)

        # Check for output files
        workspace_path = Path(WORKSPACE_DIR)
        if workspace_path.exists():
            markdown_files = list(workspace_path.glob("**/*.md"))
            if markdown_files:
                print(f"\nGenerated markdown files:")
                for md_file in markdown_files:
                    print(f"  - {md_file}")
                    print(f"\nPreview of {md_file.name}:")
                    print("-" * 80)
                    content = md_file.read_text()
                    # Show first 500 characters
                    preview = content[:500]
                    print(preview)
                    if len(content) > 500:
                        print(f"\n... ({len(content) - 500} more characters)")
                    print("-" * 80)
            else:
                print("\nNo markdown files found in workspace.")

        return 0

    except subprocess.TimeoutExpired:
        print("\nError: Process termination timed out")
        if process.poll() is None:
            process.kill()
        return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user, cleaning up...")
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
        return 1

if __name__ == "__main__":
    exit(main())
