"""
ai4sustainablex — Cloud LLM Providers
OpenAI, Anthropic Claude, DeepSeek, Google Gemini, Kimi K2
All cloud providers follow the BaseLLMProvider interface.
"""

import os
from typing import Any, Dict, List, Optional, Generator

import requests

from .base_provider import BaseLLMProvider, ProviderConfig, ProviderType


# ─── OpenAI Provider ───────────────────────────────────────────

class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider (GPT-4, GPT-3.5, etc.).
    Requires OPENAI_API_KEY environment variable or passed config.
    Base URL can be overridden for OpenAI-compatible proxies.
    """

    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("OPENAI_API_KEY", "")
            config = ProviderConfig(
                name="openai",
                provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL,
                base_url=self.DEFAULT_BASE_URL,
                api_key=api_key,
                temperature=0.2,
                max_tokens=4096,
            )
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] OpenAI API key not configured. Set OPENAI_API_KEY or configure in setup."

        try:
            url = f"{self._base_url}/chat/completions"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                },
                timeout=120,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[OpenAI Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[OpenAI Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] OpenAI API key not configured."
            return

        try:
            url = f"{self._base_url}/chat/completions"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "stream": True,
                },
                stream=True,
                timeout=120,
            )
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue
        except Exception as e:
            yield f"[Stream Error]: {str(e)}"

    def list_models(self) -> List[str]:
        default_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-mini", "o1-preview"]
        if not self._api_key:
            return default_models
        try:
            resp = requests.get(
                f"{self._base_url}/models",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                models = [m["id"] for m in resp.json().get("data", []) if m["id"].startswith(("gpt", "o1"))]
                return models or default_models
        except Exception:
            pass
        return default_models

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── Anthropic Claude Provider ─────────────────────────────────

class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude LLM provider.
    Requires ANTHROPIC_API_KEY environment variable or passed config.
    Supports Claude 3.5 Sonnet, Claude 3 Opus, etc.
    """

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_BASE_URL = "https://api.anthropic.com/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            config = ProviderConfig(
                name="anthropic",
                provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL,
                base_url=self.DEFAULT_BASE_URL,
                api_key=api_key,
                temperature=0.2,
                max_tokens=4096,
            )
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] Anthropic API key not configured."

        try:
            url = f"{self._base_url}/messages"
            headers = {
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            body = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                body["system"] = system_prompt

            resp = requests.post(url, headers=headers, json=body, timeout=120)
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"]
            return f"[Claude Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Claude Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] Anthropic API key not configured."
            return

        try:
            url = f"{self._base_url}/messages"
            headers = {
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            body = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            }
            if system_prompt:
                body["system"] = system_prompt

            resp = requests.post(url, headers=headers, json=body, stream=True, timeout=120)
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            import json
                            event = json.loads(data)
                            if event["type"] == "content_block_delta":
                                yield event["delta"].get("text", "")
                        except Exception:
                            continue
        except Exception as e:
            yield f"[Stream Error]: {str(e)}"

    def list_models(self) -> List[str]:
        return ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307",
                "claude-3-sonnet-20240229", "claude-2.1"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── DeepSeek Provider ─────────────────────────────────────────

class DeepSeekProvider(BaseLLMProvider):
    """
    DeepSeek LLM provider.
    Requires DEEPSEEK_API_KEY environment variable.
    Base URL: https://api.deepseek.com/v1
    """

    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            config = ProviderConfig(
                name="deepseek",
                provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL,
                base_url=self.DEFAULT_BASE_URL,
                api_key=api_key,
                temperature=0.2,
                max_tokens=4096,
            )
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] DeepSeek API key not configured."

        try:
            url = f"{self._base_url}/chat/completions"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                },
                timeout=120,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[DeepSeek Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[DeepSeek Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] DeepSeek API key not configured."
            return

        try:
            url = f"{self._base_url}/chat/completions"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "stream": True,
                },
                stream=True,
                timeout=120,
            )
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue
        except Exception as e:
            yield f"[Stream Error]: {str(e)}"

    def list_models(self) -> List[str]:
        return ["deepseek-chat", "deepseek-reasoner"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── Google Gemini Provider ────────────────────────────────────

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini LLM provider.
    Requires GEMINI_API_KEY environment variable.
    """

    DEFAULT_MODEL = "gemini-2.0-flash"
    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("GEMINI_API_KEY", "")
            config = ProviderConfig(
                name="gemini",
                provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL,
                base_url=self.DEFAULT_BASE_URL,
                api_key=api_key,
                temperature=0.2,
                max_tokens=4096,
            )
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] Gemini API key not configured."

        try:
            # Gemini combines system + prompt into contents
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            url = f"{self._base_url}/models/{self.config.model}:generateContent"
            resp = requests.post(
                url,
                params={"key": self._api_key},
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": self.config.temperature,
                        "maxOutputTokens": self.config.max_tokens,
                    },
                },
                timeout=120,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            return f"[Gemini Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Gemini Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] Gemini API key not configured."
            return

        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            url = f"{self._base_url}/models/{self.config.model}:streamGenerateContent"
            resp = requests.post(
                url,
                params={"alt": "sse", "key": self._api_key},
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": self.config.temperature,
                        "maxOutputTokens": self.config.max_tokens,
                    },
                },
                stream=True,
                timeout=120,
            )
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            import json
                            chunk = json.loads(data)
                            parts = chunk.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                            for part in parts:
                                if "text" in part:
                                    yield part["text"]
                        except Exception:
                            continue
        except Exception as e:
            yield f"[Stream Error]: {str(e)}"

    def list_models(self) -> List[str]:
        return ["gemini-2.0-flash", "gemini-2.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── Kimi K2 Provider ──────────────────────────────────────────

class KimiProvider(BaseLLMProvider):
    """
    Kimi (Moonshot AI) LLM provider — Kimi K2 model.
    Requires KIMI_API_KEY environment variable.
    Base URL: https://api.moonshot.cn/v1
    """

    DEFAULT_MODEL = "moonshot-v1-8k"
    DEFAULT_BASE_URL = "https://api.moonshot.cn/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("KIMI_API_KEY", "")
            config = ProviderConfig(
                name="kimi",
                provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL,
                base_url=self.DEFAULT_BASE_URL,
                api_key=api_key,
                temperature=0.2,
                max_tokens=4096,
            )
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] Kimi API key not configured."

        try:
            url = f"{self._base_url}/chat/completions"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                },
                timeout=120,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[Kimi Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Kimi Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] Kimi API key not configured."
            return

        try:
            url = f"{self._base_url}/chat/completions"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "stream": True,
                },
                stream=True,
                timeout=120,
            )
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue
        except Exception as e:
            yield f"[Stream Error]: {str(e)}"

    def list_models(self) -> List[str]:
        return ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k", "kimi-k2"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── xAI Grok Provider ─────────────────────────────────────────

class GrokProvider(BaseLLMProvider):
    """xAI Grok provider. OpenAI-compatible. Requires XAI_API_KEY."""

    DEFAULT_MODEL = "grok-2-1212"
    DEFAULT_BASE_URL = "https://api.x.ai/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("XAI_API_KEY", "")
            config = ProviderConfig(name="grok", provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL, base_url=self.DEFAULT_BASE_URL, api_key=api_key,
                temperature=0.2, max_tokens=4096)
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] xAI API key not configured. Set XAI_API_KEY."
        try:
            url = f"{self._base_url}/chat/completions"
            messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
            messages.append({"role": "user", "content": prompt})
            resp = requests.post(url, headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self.config.model, "messages": messages,
                      "temperature": self.config.temperature, "max_tokens": self.config.max_tokens}, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[Grok Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Grok Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] xAI API key not configured."; return
        yield self.generate(prompt, system_prompt)

    def list_models(self) -> List[str]:
        return ["grok-2-1212", "grok-2-vision-1212", "grok-beta"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── Groq Provider ─────────────────────────────────────────────

class GroqProvider(BaseLLMProvider):
    """Groq ultra-fast inference. OpenAI-compatible. Requires GROQ_API_KEY."""

    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("GROQ_API_KEY", "")
            config = ProviderConfig(name="groq", provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL, base_url=self.DEFAULT_BASE_URL, api_key=api_key,
                temperature=0.2, max_tokens=4096)
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] Groq API key not configured. Set GROQ_API_KEY."
        try:
            url = f"{self._base_url}/chat/completions"
            messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
            messages.append({"role": "user", "content": prompt})
            resp = requests.post(url, headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self.config.model, "messages": messages,
                      "temperature": self.config.temperature, "max_tokens": self.config.max_tokens}, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[Groq Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Groq Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] Groq API key not configured."; return
        yield self.generate(prompt, system_prompt)

    def list_models(self) -> List[str]:
        return ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── Sakana Fugu Provider (Japanese-optimized) ─────────────────

class FuguProvider(BaseLLMProvider):
    """Sakana AI Fugu — Japanese-optimized. Requires FUGU_API_KEY."""

    DEFAULT_MODEL = "fugu-mpt-7b"
    DEFAULT_BASE_URL = "https://api.sakana.ai/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("FUGU_API_KEY", "")
            config = ProviderConfig(name="fugu", provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL, base_url=self.DEFAULT_BASE_URL, api_key=api_key,
                temperature=0.2, max_tokens=4096)
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] Fugu API key not configured. Set FUGU_API_KEY."
        try:
            url = f"{self._base_url}/chat/completions"
            messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
            messages.append({"role": "user", "content": prompt})
            resp = requests.post(url, headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self.config.model, "messages": messages,
                      "temperature": self.config.temperature, "max_tokens": self.config.max_tokens}, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[Fugu Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Fugu Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] Fugu API key not configured."; return
        yield self.generate(prompt, system_prompt)

    def list_models(self) -> List[str]:
        return ["fugu-mpt-7b", "fugu-mpt-7b-instruct"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── OpenRouter Provider ───────────────────────────────────────

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter unified API for 200+ models. Requires OPENROUTER_API_KEY."""

    DEFAULT_MODEL = "openai/gpt-4o-mini"
    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("OPENROUTER_API_KEY", "")
            config = ProviderConfig(name="openrouter", provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL, base_url=self.DEFAULT_BASE_URL, api_key=api_key,
                temperature=0.2, max_tokens=4096)
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] OpenRouter API key not configured. Set OPENROUTER_API_KEY."
        try:
            url = f"{self._base_url}/chat/completions"
            messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
            messages.append({"role": "user", "content": prompt})
            resp = requests.post(url,
                headers={"Authorization": f"Bearer {self._api_key}",
                         "HTTP-Referer": "https://sustainablex.in", "X-Title": "ai4sustainablex"},
                json={"model": self.config.model, "messages": messages,
                      "temperature": self.config.temperature, "max_tokens": self.config.max_tokens}, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[OpenRouter Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[OpenRouter Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] OpenRouter API key not configured."; return
        yield self.generate(prompt, system_prompt)

    def list_models(self) -> List[str]:
        return ["openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet",
                "google/gemini-2.0-flash-001", "meta-llama/llama-3.3-70b-instruct",
                "deepseek/deepseek-chat", "qwen/qwen-2.5-72b-instruct"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── GLM Provider (Zhipu AI) ───────────────────────────────────

class GLMProvider(BaseLLMProvider):
    """GLM provider (Zhipu AI / ChatGLM). Requires GLM_API_KEY."""

    DEFAULT_MODEL = "glm-4-plus"
    DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("GLM_API_KEY", "")
            config = ProviderConfig(name="glm", provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL, base_url=self.DEFAULT_BASE_URL, api_key=api_key,
                temperature=0.2, max_tokens=4096)
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] GLM API key not configured. Set GLM_API_KEY."
        try:
            url = f"{self._base_url}/chat/completions"
            messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
            messages.append({"role": "user", "content": prompt})
            resp = requests.post(url, headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self.config.model, "messages": messages,
                      "temperature": self.config.temperature, "max_tokens": self.config.max_tokens}, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[GLM Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[GLM Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] GLM API key not configured."; return
        yield self.generate(prompt, system_prompt)

    def list_models(self) -> List[str]:
        return ["glm-4-plus", "glm-4-flash", "glm-4-long", "chatglm3-6b"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)


# ─── Qwen Provider (Alibaba) ───────────────────────────────────

class QwenProvider(BaseLLMProvider):
    """Qwen provider (Alibaba Tongyi Qianwen). Requires QWEN_API_KEY."""

    DEFAULT_MODEL = "qwen2.5-72b-instruct"
    DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            api_key = os.getenv("QWEN_API_KEY", os.getenv("DASHSCOPE_API_KEY", ""))
            config = ProviderConfig(name="qwen", provider_type=ProviderType.CLOUD,
                model=self.DEFAULT_MODEL, base_url=self.DEFAULT_BASE_URL, api_key=api_key,
                temperature=0.2, max_tokens=4096)
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._api_key = config.api_key
        self._available = bool(self._api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self._api_key:
            return "[Error] Qwen API key not configured. Set QWEN_API_KEY."
        try:
            url = f"{self._base_url}/chat/completions"
            messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
            messages.append({"role": "user", "content": prompt})
            resp = requests.post(url, headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self.config.model, "messages": messages,
                      "temperature": self.config.temperature, "max_tokens": self.config.max_tokens}, timeout=120)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"[Qwen Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Qwen Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[Error] Qwen API key not configured."; return
        yield self.generate(prompt, system_prompt)

    def list_models(self) -> List[str]:
        return ["qwen2.5-72b-instruct", "qwen2.5-32b-instruct", "qwen-max", "qwen-plus"]

    def health_check(self) -> bool:
        return self._available and bool(self._api_key)
