# ai4sustainablex — LLM Provider Package
# 12 providers: Ollama, OpenAI, Anthropic, DeepSeek, Gemini, Kimi K2,
# xAI Grok, Groq, Sakana Fugu, OpenRouter, GLM (Zhipu), Qwen (Alibaba

from .base_provider import BaseLLMProvider, ProviderConfig, ProviderType
from .ollama_provider import OllamaProvider
from .cloud_providers import (
    OpenAIProvider,
    AnthropicProvider,
    DeepSeekProvider,
    GeminiProvider,
    KimiProvider,
    GrokProvider,
    GroqProvider,
    FuguProvider,
    OpenRouterProvider,
    GLMProvider,
    QwenProvider,
)

__all__ = [
    "BaseLLMProvider",
    "ProviderConfig",
    "ProviderType",
    "OllamaProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "DeepSeekProvider",
    "GeminiProvider",
    "KimiProvider",
    "GrokProvider",
    "GroqProvider",
    "FuguProvider",
    "OpenRouterProvider",
    "GLMProvider",
    "QwenProvider",
]

PROVIDER_REGISTRY = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "deepseek": DeepSeekProvider,
    "gemini": GeminiProvider,
    "kimi": KimiProvider,
    "grok": GrokProvider,
    "groq": GroqProvider,
    "fugu": FuguProvider,
    "openrouter": OpenRouterProvider,
    "glm": GLMProvider,
    "qwen": QwenProvider,
}
