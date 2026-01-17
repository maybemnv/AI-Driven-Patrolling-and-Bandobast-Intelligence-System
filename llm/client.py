"""LLM client wrapper for Ollama with retry logic."""

import json
import time
from typing import Optional, Generator
from dataclasses import dataclass

import requests

from config import get_settings


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model: str
    tokens_prompt: int
    tokens_completion: int
    duration_ms: float
    

class OllamaClient:
    """Ollama API client with retry and timeout handling."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
        timeout: int = 120,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.default_options = {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 1000,
        }
    
    def _request(self, endpoint: str, payload: dict) -> dict:
        """Make request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                resp = requests.post(url, json=payload, timeout=self.timeout)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"Ollama request timed out after {self.timeout}s")
                time.sleep(2 ** attempt)
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries - 1:
                    raise ConnectionError("Cannot connect to Ollama. Is it running?")
                time.sleep(2 ** attempt)
            except requests.exceptions.HTTPError as e:
                raise RuntimeError(f"Ollama API error: {e}")
        
        raise RuntimeError("Max retries exceeded")
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate completion."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
            },
        }
        
        if system:
            payload["system"] = system
        
        start = time.perf_counter()
        result = self._request("/api/generate", payload)
        duration = (time.perf_counter() - start) * 1000
        
        return LLMResponse(
            content=result.get("response", ""),
            model=result.get("model", self.model),
            tokens_prompt=result.get("prompt_eval_count", 0),
            tokens_completion=result.get("eval_count", 0),
            duration_ms=duration,
        )
    
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Chat completion with messages."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        
        start = time.perf_counter()
        result = self._request("/api/chat", payload)
        duration = (time.perf_counter() - start) * 1000
        
        return LLMResponse(
            content=result.get("message", {}).get("content", ""),
            model=result.get("model", self.model),
            tokens_prompt=result.get("prompt_eval_count", 0),
            tokens_completion=result.get("eval_count", 0),
            duration_ms=duration,
        )
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> list[str]:
        """List available models."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []


def get_llm_client(model: str = "llama3.2") -> OllamaClient:
    """Get configured LLM client."""
    settings = get_settings()
    return OllamaClient(
        base_url=getattr(settings, "ollama_url", "http://localhost:11434"),
        model=model,
    )
