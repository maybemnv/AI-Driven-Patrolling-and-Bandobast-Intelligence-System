"""LangChain-based LLM client with Groq support."""

from typing import Optional
from dataclasses import dataclass

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from config import get_settings


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model: str
    tokens_prompt: int
    tokens_completion: int
    duration_ms: float


class GroqLangChainClient:
    """LangChain wrapper for Groq API."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.3,
    ):
        from groq import Groq
        self.groq_client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
    
    def invoke(self, messages: list[dict], **kwargs) -> str:
        """Invoke the model with messages."""
        import time
        start = time.perf_counter()
        
        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", 1000),
        )
        
        self._last_duration = (time.perf_counter() - start) * 1000
        self._last_usage = response.usage
        
        return response.choices[0].message.content or ""
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate completion using LangChain pattern."""
        import time
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        start = time.perf_counter()
        content = self.invoke(messages, temperature=temperature, max_tokens=max_tokens)
        duration = (time.perf_counter() - start) * 1000
        
        usage = getattr(self, "_last_usage", None)
        
        return LLMResponse(
            content=content,
            model=self.model,
            tokens_prompt=usage.prompt_tokens if usage else 0,
            tokens_completion=usage.completion_tokens if usage else 0,
            duration_ms=duration,
        )
    
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Chat completion with messages."""
        import time
        start = time.perf_counter()
        
        content = self.invoke(messages, temperature=temperature, max_tokens=max_tokens)
        duration = (time.perf_counter() - start) * 1000
        
        usage = getattr(self, "_last_usage", None)
        
        return LLMResponse(
            content=content,
            model=self.model,
            tokens_prompt=usage.prompt_tokens if usage else 0,
            tokens_completion=usage.completion_tokens if usage else 0,
            duration_ms=duration,
        )
    
    def is_available(self) -> bool:
        """Check if API is accessible."""
        try:
            self.groq_client.models.list()
            return True
        except Exception:
            return False
    
    def list_models(self) -> list[str]:
        """List available models."""
        try:
            response = self.groq_client.models.list()
            return [m.id for m in response.data]
        except Exception:
            return []


def create_chain(system_prompt: str, llm_client: GroqLangChainClient):
    """Create a LangChain-style chain with prompt template."""
    
    def chain_invoke(user_input: str, **kwargs) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
        return llm_client.invoke(messages, **kwargs)
    
    return chain_invoke


def get_llm_client(model: Optional[str] = None):
    """Get LangChain-compatible LLM client."""
    settings = get_settings()
    
    api_key = getattr(settings, "groq_api_key", None)
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")
    
    model = model or getattr(settings, "groq_model", "llama-3.1-8b-instant")
    
    return GroqLangChainClient(api_key=api_key, model=model)
