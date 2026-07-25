"""
ai4sustainablex — Abstract Base LLM Provider
All LLM providers (Ollama, OpenAI, Anthropic, DeepSeek, Gemini, Kimi K2)
inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generator
from dataclasses import dataclass, field
from enum import Enum


class ProviderType(Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    name: str
    provider_type: ProviderType
    model: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseLLMProvider(ABC):
    """
    Abstract base for all LLM providers in ai4sustainablex.

    Each provider implements:
    - generate(): Text generation with prompt
    - generate_with_context(): RAG-enhanced generation
    - stream(): Streaming generation
    - list_models(): Available models
    - health_check(): Provider availability
    """

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._available = False

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system-level instruction

        Returns:
            Generated text response
        """
        ...

    @abstractmethod
    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """
        Stream a response from the LLM token by token.

        Args:
            prompt: The user prompt
            system_prompt: Optional system-level instruction

        Yields:
            Text chunks as they are generated
        """
        ...

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Return available models for this provider.

        Returns:
            List of model identifiers
        """
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the provider is available and operational.

        Returns:
            True if the provider is reachable and working
        """
        ...

    def generate_with_context(self, query: str, context_chunks: List[str],
                              template_prompt: Optional[str] = None,
                              max_context_tokens: int = 4000) -> str:
        """
        RAG-enhanced generation: inject retrieved context into the prompt.

        Args:
            query: The user's question
            context_chunks: Retrieved document chunks from RAG engine
            template_prompt: Optional template-specific system prompt
            max_context_tokens: Max context window size in tokens

        Returns:
            Generated answer grounded in the provided context
        """
        # Build context section
        context_text = "\n\n---\n\n".join([
            f"[Source {i+1}]: {chunk}"
            for i, chunk in enumerate(context_chunks[:10])
        ])

        # Truncate context if too long
        if len(context_text) > max_context_tokens * 4:
            context_text = context_text[:max_context_tokens * 4]
            context_text += "\n\n... [context truncated to fit model limits]"

        # Default system prompt if none provided
        if template_prompt:
            system = template_prompt
        else:
            system = (
                "You are ai4sustainablex, an expert ESG and sustainability reporting assistant. "
                "Answer the user's question based ONLY on the provided context. "
                "If the context does not contain enough information to answer, say so clearly. "
                "Always cite source numbers when referencing specific data. "
                "Be precise, factual, and avoid hallucination. "
                "Format your answer in clear sections with markdown headings where appropriate."
            )

        # Build full prompt
        full_prompt = (
            f"{system}\n\n"
            f"CONTEXT DOCUMENTS:\n{context_text}\n\n"
            f"USER QUERY: {query}\n\n"
            f"Answer based on the context above:"
        )

        return self.generate(full_prompt)

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 characters ≈ 1 token)."""
        return len(text) // 4

    def get_config_info(self) -> Dict[str, Any]:
        """Return provider configuration as a dictionary (no secrets)."""
        return {
            "name": self.config.name,
            "type": self.config.provider_type.value,
            "model": self.config.model,
            "base_url": self.config.base_url,
            "has_api_key": bool(self.config.api_key),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "available": self._available,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(model='{self.config.model}', available={self._available})>"