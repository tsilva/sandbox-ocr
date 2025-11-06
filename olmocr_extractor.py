#!/usr/bin/env python3
"""
Portable OLMoCR PDF-to-Markdown Extractor
==========================================

A self-contained module for converting PDFs to markdown using OLMoCR via DeepInfra.

Dependencies:
    - olmocr (the OLMoCR library)
    - python-dotenv (optional, for loading .env files)

Usage:
    from olmocr_extractor import OLMoCRExtractor

    # Initialize extractor
    extractor = OLMoCRExtractor(
        api_key="your_deepinfra_api_key",
        workspace_dir="./output"
    )

    # Convert single PDF
    result = extractor.convert_pdf("document.pdf")
    print(f"Markdown saved to: {result['markdown_file']}")

    # Convert multiple PDFs
    results = extractor.convert_pdfs(["doc1.pdf", "doc2.pdf"])

    # Get markdown content
    content = extractor.get_markdown_content(result['markdown_file'])
"""

import os
import subprocess
import signal
import time
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Union, List, Dict, Any


class OLMoCRExtractor:
    """
    Portable OCR extractor using OLMoCR with DeepInfra remote inference.

    Converts PDF documents to markdown using the allenai/olmOCR-2-7B-1025 model,
    which handles equations, tables, complex layouts, handwriting, and multi-column documents.
    """

    DEFAULT_ENDPOINT = "https://api.deepinfra.com/v1/openai"
    DEFAULT_MODEL = "allenai/olmOCR-2-7B-1025"

    def __init__(
        self,
        api_key: Optional[str] = None,
        workspace_dir: str = "./workspace",
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize the OLMoCR extractor.

        Args:
            api_key: DeepInfra API key. If None, will try to load from DEEPINFRA_API_KEY env var.
            workspace_dir: Directory where output files will be saved.
            endpoint: API endpoint URL. Defaults to DeepInfra's OpenAI-compatible endpoint.
            model: Model name to use. Defaults to allenai/olmOCR-2-7B-1025.
            verbose: Whether to print progress information.

        Raises:
            ValueError: If API key is not provided and not found in environment.
        """
        self.api_key = api_key or os.getenv("DEEPINFRA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it via api_key parameter or "
                "set DEEPINFRA_API_KEY environment variable."
            )

        self.workspace_dir = Path(workspace_dir)
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        self.model = model or self.DEFAULT_MODEL
        self.verbose = verbose

        # Create workspace directory if it doesn't exist
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def convert_pdf(
        self,
        pdf_path: Union[str, Path],
        output_name: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convert a single PDF to markdown.

        Args:
            pdf_path: Path to the PDF file.
            output_name: Optional custom name for output (without extension).
            timeout: Maximum seconds to wait for conversion. None for no timeout.

        Returns:
            Dictionary with conversion results:
                - success: bool
                - markdown_file: Path to generated markdown file
                - content: Markdown content as string
                - error: Error message if conversion failed

        Raises:
            FileNotFoundError: If PDF file doesn't exist.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        return self._run_conversion([str(pdf_path)], timeout=timeout)

    def convert_pdfs(
        self,
        pdf_paths: List[Union[str, Path]],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convert multiple PDFs to markdown.

        Args:
            pdf_paths: List of paths to PDF files.
            timeout: Maximum seconds to wait for conversion. None for no timeout.

        Returns:
            Dictionary with conversion results:
                - success: bool
                - markdown_files: List of paths to generated markdown files
                - contents: Dict mapping file paths to markdown content
                - error: Error message if conversion failed

        Raises:
            FileNotFoundError: If any PDF file doesn't exist.
        """
        pdf_paths = [Path(p) for p in pdf_paths]

        # Validate all files exist
        for pdf_path in pdf_paths:
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")

        return self._run_conversion([str(p) for p in pdf_paths], timeout=timeout)

    def convert_pdfs_colocated(
        self,
        pdf_paths: List[Union[str, Path]],
        timeout_per_pdf: Optional[int] = None,
        cleanup_temp: bool = True
    ) -> Dict[str, Any]:
        """
        Convert multiple PDFs to markdown, placing output files alongside each PDF.

        This method processes each PDF individually using a unique temporary workspace,
        then moves the generated markdown file to the same directory as the source PDF.
        This approach ensures no conflicts and enables parallel processing.

        Args:
            pdf_paths: List of paths to PDF files.
            timeout_per_pdf: Maximum seconds to wait for each PDF conversion. None for no timeout.
            cleanup_temp: Whether to clean up temporary workspace directories after conversion.

        Returns:
            Dictionary with conversion results:
                - success: bool - True if all conversions succeeded
                - results: Dict mapping PDF paths to their results
                    Each result contains:
                        - success: bool
                        - pdf_path: str - Original PDF path
                        - markdown_file: str - Path to generated markdown file (colocated with PDF)
                        - content: str - Markdown content
                        - error: str (if failed)
                - failed_count: int - Number of failed conversions
                - success_count: int - Number of successful conversions

        Raises:
            FileNotFoundError: If any PDF file doesn't exist.
        """
        pdf_paths = [Path(p).resolve() for p in pdf_paths]

        # Validate all files exist
        for pdf_path in pdf_paths:
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if self.verbose:
            print("=" * 80)
            print("OLMoCR Co-located PDF to Markdown Conversion")
            print("=" * 80)
            print(f"Endpoint: {self.endpoint}")
            print(f"Model: {self.model}")
            print(f"Input PDFs: {len(pdf_paths)}")
            for pdf in pdf_paths:
                print(f"  - {pdf}")
            print("=" * 80)
            print()

        results = {}
        success_count = 0
        failed_count = 0

        # Process each PDF individually
        for idx, pdf_path in enumerate(pdf_paths, 1):
            if self.verbose:
                print(f"\n[{idx}/{len(pdf_paths)}] Processing: {pdf_path.name}")
                print("-" * 80)

            # Create unique temporary workspace for this PDF
            temp_workspace = Path(tempfile.mkdtemp(prefix=f"olmocr_{pdf_path.stem}_"))

            try:
                # Run conversion with temporary workspace
                result = self._run_conversion_single(
                    str(pdf_path),
                    temp_workspace,
                    timeout=timeout_per_pdf
                )

                if result["success"]:
                    # File is already in the right place (colocated with PDF)
                    result["pdf_path"] = str(pdf_path)
                    success_count += 1

                    if self.verbose:
                        print(f"✓ Markdown saved to: {result['markdown_file']}")
                else:
                    failed_count += 1
                    result["pdf_path"] = str(pdf_path)

                results[str(pdf_path)] = result

            except Exception as e:
                failed_count += 1
                results[str(pdf_path)] = {
                    "success": False,
                    "pdf_path": str(pdf_path),
                    "error": str(e)
                }
                if self.verbose:
                    print(f"✗ Error processing {pdf_path.name}: {e}")

            finally:
                # Clean up temporary workspace
                if cleanup_temp and temp_workspace.exists():
                    try:
                        shutil.rmtree(temp_workspace)
                    except Exception as e:
                        if self.verbose:
                            print(f"Warning: Failed to clean up temp workspace: {e}")

        if self.verbose:
            print()
            print("=" * 80)
            print(f"✓ Batch conversion completed!")
            print(f"  Success: {success_count}/{len(pdf_paths)}")
            print(f"  Failed: {failed_count}/{len(pdf_paths)}")
            print("=" * 80)

        return {
            "success": failed_count == 0,
            "results": results,
            "success_count": success_count,
            "failed_count": failed_count
        }

    def _run_conversion_single(
        self,
        pdf_path: str,
        workspace_dir: Path,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Internal method to run the OLMoCR pipeline for a single PDF.

        Args:
            pdf_path: Path to PDF file.
            workspace_dir: Workspace directory for this conversion.
            timeout: Maximum seconds to wait for conversion.

        Returns:
            Dictionary with conversion results.
        """
        # Create workspace directory
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            "python", "-m", "olmocr.pipeline",
            str(workspace_dir),
            "--server", self.endpoint,
            "--api_key", self.api_key,
            "--model", self.model,
            "--markdown",
            "--pdfs", pdf_path
        ]

        try:
            # Run the pipeline
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Monitor completion
            start_time = time.time()
            queue_empty_count = 0
            markdown_written = False

            for line in iter(process.stderr.readline, ''):
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    process.send_signal(signal.SIGTERM)
                    process.wait(timeout=5)
                    return {
                        "success": False,
                        "error": f"Conversion timed out after {timeout} seconds"
                    }

                # Show important log lines (only in verbose mode)
                if self.verbose and any(keyword in line for keyword in
                    ['ERROR', 'WARNING', 'Writing', 'markdown']):
                    print(line.rstrip())

                # Track completion signals
                if 'Writing' in line and 'markdown' in line:
                    markdown_written = True

                if 'Queue remaining: 0' in line and markdown_written:
                    queue_empty_count += 1
                    # After seeing queue empty 3 times, we're done
                    if queue_empty_count >= 3:
                        time.sleep(0.5)
                        process.send_signal(signal.SIGTERM)
                        process.wait(timeout=5)
                        break

            # Ensure process is terminated
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)

            # Find the generated markdown file
            # The olmocr pipeline writes markdown files to the same directory as the PDF
            pdf_path_obj = Path(pdf_path)
            expected_md_file = pdf_path_obj.parent / f"{pdf_path_obj.stem}.md"

            # Wait a bit for file to be fully written
            max_wait = 5  # seconds
            wait_interval = 0.5
            waited = 0

            while waited < max_wait:
                if expected_md_file.exists():
                    # Ensure file is fully written by checking size stability
                    try:
                        size1 = expected_md_file.stat().st_size
                        time.sleep(0.2)
                        size2 = expected_md_file.stat().st_size
                        if size1 == size2 and size1 > 0:
                            content = expected_md_file.read_text()
                            return {
                                "success": True,
                                "markdown_file": str(expected_md_file),
                                "content": content
                            }
                    except Exception:
                        pass

                time.sleep(wait_interval)
                waited += wait_interval

            # Check one more time after waiting
            if expected_md_file.exists():
                try:
                    content = expected_md_file.read_text()
                    return {
                        "success": True,
                        "markdown_file": str(expected_md_file),
                        "content": content
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to read markdown file: {e}"
                    }

            # Also check workspace/markdown as fallback
            markdown_dir = workspace_dir / "markdown"
            if markdown_dir.exists():
                markdown_files = list(markdown_dir.glob("*.md"))
                if markdown_files:
                    md_file = markdown_files[0]
                    try:
                        content = md_file.read_text()
                        return {
                            "success": True,
                            "markdown_file": str(md_file),
                            "content": content
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Failed to read markdown file: {e}"
                        }

            return {
                "success": False,
                "error": "No markdown file generated"
            }

        except subprocess.TimeoutExpired:
            if process.poll() is None:
                process.kill()
            return {
                "success": False,
                "error": "Process termination timed out"
            }

        except Exception as e:
            if 'process' in locals() and process.poll() is None:
                process.terminate()
            return {
                "success": False,
                "error": str(e)
            }

    def _run_conversion(
        self,
        pdf_paths: List[str],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Internal method to run the OLMoCR pipeline.

        Args:
            pdf_paths: List of PDF file paths to convert.
            timeout: Maximum seconds to wait for conversion.

        Returns:
            Dictionary with conversion results.
        """
        if self.verbose:
            print("=" * 80)
            print("OLMoCR PDF to Markdown Conversion")
            print("=" * 80)
            print(f"Endpoint: {self.endpoint}")
            print(f"Model: {self.model}")
            print(f"Input PDFs: {len(pdf_paths)}")
            for pdf in pdf_paths:
                print(f"  - {pdf}")
            print(f"Output directory: {self.workspace_dir}")
            print("=" * 80)
            print()

        # Build command
        cmd = [
            "python", "-m", "olmocr.pipeline",
            str(self.workspace_dir),
            "--server", self.endpoint,
            "--api_key", self.api_key,
            "--model", self.model,
            "--markdown",
        ]

        # Add all PDF paths
        for pdf in pdf_paths:
            cmd.extend(["--pdfs", pdf])

        try:
            # Run the pipeline
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Monitor completion
            start_time = time.time()
            queue_empty_count = 0
            markdown_written = False

            for line in iter(process.stderr.readline, ''):
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    process.send_signal(signal.SIGTERM)
                    process.wait(timeout=5)
                    return {
                        "success": False,
                        "error": f"Conversion timed out after {timeout} seconds"
                    }

                # Show important log lines
                if self.verbose and any(keyword in line for keyword in
                    ['INFO', 'ERROR', 'WARNING', 'Queue remaining', 'Writing', 'markdown']):
                    print(line.rstrip())

                # Track completion signals
                if 'Writing' in line and 'markdown' in line:
                    markdown_written = True

                if 'Queue remaining: 0' in line and markdown_written:
                    queue_empty_count += 1
                    # After seeing queue empty 3 times, we're done
                    if queue_empty_count >= 3:
                        if self.verbose:
                            print("\n✓ Processing complete, shutting down pipeline...")
                        time.sleep(0.5)
                        process.send_signal(signal.SIGTERM)
                        process.wait(timeout=5)
                        break

            # Ensure process is terminated
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)

            # Collect results
            markdown_dir = self.workspace_dir / "markdown"
            markdown_files = []
            contents = {}

            if markdown_dir.exists():
                markdown_files = sorted(markdown_dir.glob("*.md"))
                for md_file in markdown_files:
                    contents[str(md_file)] = md_file.read_text()

            if self.verbose:
                print()
                print("=" * 80)
                print("✓ Conversion completed successfully!")
                print("=" * 80)
                print(f"\nGenerated {len(markdown_files)} markdown file(s):")
                for md_file in markdown_files:
                    print(f"  - {md_file}")

            # Return results based on single vs multiple files
            if len(markdown_files) == 1:
                md_file = markdown_files[0]
                return {
                    "success": True,
                    "markdown_file": str(md_file),
                    "content": contents[str(md_file)]
                }
            else:
                return {
                    "success": True,
                    "markdown_files": [str(f) for f in markdown_files],
                    "contents": contents
                }

        except subprocess.TimeoutExpired:
            if process.poll() is None:
                process.kill()
            return {
                "success": False,
                "error": "Process termination timed out"
            }

        except KeyboardInterrupt:
            if self.verbose:
                print("\n\nInterrupted by user, cleaning up...")
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            return {
                "success": False,
                "error": "Conversion interrupted by user"
            }

        except Exception as e:
            if 'process' in locals() and process.poll() is None:
                process.terminate()
            return {
                "success": False,
                "error": str(e)
            }

    def get_markdown_content(self, markdown_path: Union[str, Path]) -> str:
        """
        Read and return the content of a markdown file.

        Args:
            markdown_path: Path to the markdown file.

        Returns:
            Markdown content as string.
        """
        return Path(markdown_path).read_text()

    def preview_markdown(
        self,
        markdown_path: Union[str, Path],
        max_chars: int = 500
    ) -> str:
        """
        Get a preview of a markdown file.

        Args:
            markdown_path: Path to the markdown file.
            max_chars: Maximum number of characters to return.

        Returns:
            Preview string with truncation notice if applicable.
        """
        content = self.get_markdown_content(markdown_path)
        if len(content) <= max_chars:
            return content
        return content[:max_chars] + f"\n\n... ({len(content) - max_chars} more characters)"


def convert_pdf_to_markdown(
    pdf_path: Union[str, Path],
    api_key: Optional[str] = None,
    workspace_dir: str = "./workspace",
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to convert a single PDF to markdown.

    Args:
        pdf_path: Path to the PDF file.
        api_key: DeepInfra API key. If None, will try to load from environment.
        workspace_dir: Directory where output files will be saved.
        verbose: Whether to print progress information.

    Returns:
        Dictionary with conversion results.
    """
    extractor = OLMoCRExtractor(
        api_key=api_key,
        workspace_dir=workspace_dir,
        verbose=verbose
    )
    return extractor.convert_pdf(pdf_path)


# Example usage and testing
if __name__ == "__main__":
    import sys

    # Try to load .env file if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if len(sys.argv) < 2:
        print("Usage: python olmocr_extractor.py <pdf_file>")
        print("\nExample:")
        print("  python olmocr_extractor.py document.pdf")
        sys.exit(1)

    pdf_file = sys.argv[1]

    try:
        # Quick conversion
        result = convert_pdf_to_markdown(pdf_file)

        if result["success"]:
            print(f"\n✓ Success! Markdown saved to: {result['markdown_file']}")
            print("\nPreview:")
            print("-" * 80)
            print(result['content'][:500])
            if len(result['content']) > 500:
                print(f"\n... ({len(result['content']) - 500} more characters)")
            print("-" * 80)
        else:
            print(f"\n✗ Error: {result['error']}")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
