#!/usr/bin/env python3
"""
OCR Provider Configurations
============================

Defines configurations for various OCR providers including OLMoCR and DeepSeek-OCR.
All providers use OpenAI-compatible API format.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OCRProvider:
    """Configuration for an OCR provider."""
    name: str
    endpoint: str
    model: str
    api_key_env_var: str
    description: str
    pricing_input: Optional[str] = None
    pricing_output: Optional[str] = None


# Predefined OCR Providers
PROVIDERS = {
    "olmocr-deepinfra": OCRProvider(
        name="OLMoCR via DeepInfra",
        endpoint="https://api.deepinfra.com/v1/openai",
        model="allenai/olmOCR-2-7B-1025",
        api_key_env_var="DEEPINFRA_API_KEY",
        description="OLMoCR model via DeepInfra. Handles equations, tables, complex layouts, handwriting, and multi-column documents.",
        pricing_input="~$0.09 per 1M input tokens",
        pricing_output="~$0.19 per 1M output tokens"
    ),

    "deepseek-vllm": OCRProvider(
        name="DeepSeek-OCR via vLLM (Self-hosted)",
        endpoint="http://localhost:8000/v1",  # Default vLLM endpoint
        model="deepseek-ai/DeepSeek-OCR",
        api_key_env_var="VLLM_API_KEY",  # Optional for self-hosted
        description="DeepSeek-OCR self-hosted via vLLM. Fast inference (~2500 tokens/s on A100-40G). Requires local GPU setup."
    ),

    "deepseek-clarifai": OCRProvider(
        name="DeepSeek-OCR via Clarifai",
        endpoint="https://api.clarifai.com/v2/models/deepseek-ocr/outputs",  # Placeholder - check actual endpoint
        model="deepseek-ai/DeepSeek-OCR",
        api_key_env_var="CLARIFAI_PAT",
        description="DeepSeek-OCR hosted by Clarifai. OpenAI-compatible API. Can process up to 200K pages per day on single A100."
    ),

    "custom": OCRProvider(
        name="Custom OpenAI-compatible endpoint",
        endpoint="",  # User must specify
        model="",     # User must specify
        api_key_env_var="CUSTOM_API_KEY",
        description="Custom OpenAI-compatible OCR endpoint"
    )
}


def get_provider(provider_name: str) -> OCRProvider:
    """
    Get a provider configuration by name.

    Args:
        provider_name: Name of the provider (e.g., 'olmocr-deepinfra', 'deepseek-vllm')

    Returns:
        OCRProvider configuration

    Raises:
        ValueError: If provider name is not found
    """
    if provider_name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {available}"
        )
    return PROVIDERS[provider_name]


def list_providers() -> dict[str, OCRProvider]:
    """Get all available provider configurations."""
    return PROVIDERS.copy()


def print_providers():
    """Print information about all available providers."""
    print("=" * 80)
    print("Available OCR Providers")
    print("=" * 80)
    print()

    for key, provider in PROVIDERS.items():
        print(f"Provider: {key}")
        print(f"  Name: {provider.name}")
        print(f"  Endpoint: {provider.endpoint}")
        print(f"  Model: {provider.model}")
        print(f"  API Key: ${provider.api_key_env_var}")
        print(f"  Description: {provider.description}")
        if provider.pricing_input:
            print(f"  Pricing: {provider.pricing_input} / {provider.pricing_output}")
        print()


if __name__ == "__main__":
    print_providers()
