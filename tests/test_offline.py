import subprocess
import sys

import pytest

from ocr_providers import get_provider
from olmocr_extractor import OLMoCRExtractor


def test_olmocr_pipeline_cli_contract_is_available() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "olmocr.pipeline", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    for flag in ("--server", "--api_key", "--model", "--markdown", "--pdfs"):
        assert flag in result.stdout


def test_self_hosted_provider_initializes_without_credentials(tmp_path) -> None:
    extractor = OLMoCRExtractor(
        provider="deepseek-vllm",
        workspace_dir=str(tmp_path),
        verbose=False,
    )

    assert extractor.endpoint == "http://localhost:8000/v1"
    assert extractor.model == "deepseek-ai/DeepSeek-OCR"
    assert extractor.api_key is None


def test_remote_provider_rejects_missing_credentials(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("DEEPINFRA_API_KEY", raising=False)

    with pytest.raises(ValueError, match="API key is required"):
        OLMoCRExtractor(workspace_dir=str(tmp_path), verbose=False)


def test_missing_input_is_rejected_before_any_request(tmp_path) -> None:
    extractor = OLMoCRExtractor(
        api_key="offline-test-key",
        workspace_dir=str(tmp_path),
        verbose=False,
    )

    with pytest.raises(FileNotFoundError, match="PDF not found"):
        extractor.convert_pdf(tmp_path / "missing.pdf")


def test_provider_lookup_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("malicious-provider")
