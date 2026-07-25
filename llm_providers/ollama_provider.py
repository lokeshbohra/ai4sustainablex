"""
ai4sustainablex — Ollama Provider (Default Local LLM)
Runs models locally via Ollama. No internet required for inference.
Default model: llama3.2:1b (can be changed during setup).
"""

import subprocess
import json
from typing import Any, Dict, List, Optional, Generator

import requests

from .base_provider import BaseLLMProvider, ProviderConfig, ProviderType


class OllamaProvider(BaseLLMProvider):
    """
    Local LLM provider using Ollama.

    Default model: llama3.2:1b (smallest, fastest)
    Supports any model available in Ollama: llama3.2, mistral, deepseek-r1, gemma, etc.

    Configuration:
        model: Ollama model tag (e.g., 'llama3.2:1b', 'llama3.2:3b', 'mistral:7b')
        base_url: Ollama API URL (default: http://localhost:11434)
        api_key: Not required (local only)
    """

    DEFAULT_MODEL = "llama3.2:1b"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(
                name="ollama",
                provider_type=ProviderType.LOCAL,
                model=self.DEFAULT_MODEL,
                base_url=self.DEFAULT_BASE_URL,
                temperature=0.2,  # Lower temp for factual ESG reporting
                max_tokens=4096,
            )
        super().__init__(config)
        self._base_url = config.base_url or self.DEFAULT_BASE_URL
        self._health_check()

    def _health_check(self):
        """Set availability status."""
        self._available = self.health_check()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using Ollama.
        Uses the /api/generate endpoint for non-streaming generation.
        """
        try:
            url = f"{self._base_url}/api/generate"
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "system": system_prompt or "",
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                    "top_p": self.config.top_p,
                },
            }
            resp = requests.post(url, json=payload, timeout=300)
            if resp.status_code == 200:
                return resp.json().get("response", "")
            return f"[Ollama Error {resp.status_code}]: {resp.text}"
        except requests.ConnectionError:
            return "[Error] Cannot connect to Ollama. Is it running? Run: ollama serve"
        except Exception as e:
            return f"[Ollama Error]: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """
        Stream response from Ollama token by token.
        Uses the /api/generate endpoint with stream=True.
        """
        try:
            url = f"{self._base_url}/api/generate"
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "system": system_prompt or "",
                "stream": True,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                    "top_p": self.config.top_p,
                },
            }
            resp = requests.post(url, json=payload, stream=True, timeout=300)
            for line in resp.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield f"[Stream Error]: {str(e)}"

    def list_models(self) -> List[str]:
        """
        List locally available Ollama models.
        Returns model tags (e.g., 'llama3.2:1b', 'mistral:7b').
        """
        try:
            url = f"{self._base_url}/api/tags"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except Exception:
            return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull (download) a model from Ollama.

        Args:
            model_name: Model tag to pull (e.g., 'llama3.2:1b')

        Returns:
            True if pull succeeded, False otherwise
        """
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=1800,  # 30 min timeout for downloads
            )
            return result.returncode == 0
        except FileNotFoundError:
            print("⚠️ Ollama not installed. Run: curl -fsSL https://ollama.com/install.sh | bash")
            return False
        except subprocess.TimeoutExpired:
            print(f"⚠️ Model pull timed out for {model_name}")
            return False

    def pull_model_streaming(self, model_name: str) -> Generator[str, None, None]:
        """
        Pull a model with streaming progress output.

        Yields:
            Progress messages as the model downloads
        """
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout
            for line in process.stdout:
                yield line.strip()
            process.wait()
        except FileNotFoundError:
            yield "⚠️ Ollama not installed."
        except Exception as e:
            yield f"⚠️ Error: {e}"

    def health_check(self) -> bool:
        """
        Check if Ollama is running and accessible.
        Also verifies the configured model is available.
        """
        try:
            # Try to reach Ollama API
            url = f"{self._base_url}/api/tags"
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                return False

            # Check if model exists; if not, auto-pull
            models = resp.json().get("models", [])
            model_names = [m["name"] for m in models]
            if self.config.model not in model_names:
                # Model not found locally — attempt to pull
                print(f"📥 Model '{self.config.model}' not found. Attempting to pull...")
                result = subprocess.run(
                    ["ollama", "pull", self.config.model],
                    capture_output=True,
                    text=True,
                    timeout=1800,
                )
                return result.returncode == 0

            return True
        except requests.ConnectionError:
            return False
        except Exception:
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """Extended config info with Ollama-specific data."""
        info = super().get_config_info()
        info.update({
            "base_url": self._base_url,
            "available_models": self.list_models() if self._available else [],
        })
        return info