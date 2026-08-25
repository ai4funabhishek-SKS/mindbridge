"""
mindbridge LLM Provider Abstraction Layer
Supports multiple LLM providers with automatic fallback chain.
"""

import os
import json
import yaml
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for a single LLM provider."""
    name: str
    enabled: bool = True
    priority: int = 1
    provider_type: str = "opencode"
    model: str = "freemodel"
    api_key_env: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_tokens: int = 4096
    temperature: float = 0.2
    fallback_models: List[str] = field(default_factory=list)
    
    # Runtime fields
    api_key: str = ""
    base_url_resolved: str = ""

    def resolve_secrets(self) -> None:
        """Resolve API keys from environment variables."""
        if self.api_key_env and not self.api_key:
            self.api_key = os.environ.get(self.api_key_env, "")
        if self.base_url:
            self.base_url_resolved = self.base_url

    def get_api_key(self) -> str:
        """Get API key, checking config first, then environment."""
        if self.api_key:
            return self.api_key
        if self.api_key_env:
            return os.environ.get(self.api_key_env, "")
        return ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "priority": self.priority,
            "provider_type": self.provider_type,
            "model": self.model,
            "api_key_env": self.api_key_env,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "fallback_models": self.fallback_models,
        }

@dataclass
class EmbeddingConfig:
    """Configuration for embedding provider."""
    provider: str = "ollama"
    model: str = "nomic-embed-text"
    base_url: str = "http://localhost:11434"
    dimensions: int = 768
    batch_size: int = 32

@dataclass
class AskModeConfig:
    """Configuration for Ask mode."""
    default_provider: str = "auto"
    max_passages: int = 12
    max_passage_chars: int = 700
    context_window: int = 4096
    temperature: float = 0.2
    fallback_context_windows: List[int] = field(default_factory=lambda: [4096, 2048, 1024])
    citation_format: str = "[S{num}]"
    save_briefings: bool = True
    briefings_dir: str = "Briefings"

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.config.resolve_secrets()
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and return response."""
        pass
    
    @abstractmethod
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Stream chat response."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    def get_model(self) -> str:
        return self.config.model
    
    def get_fallback_models(self) -> List[str]:
        return self.config.fallback_models

class OpenCodeProvider(LLMProvider):
    """OpenCode Zen provider (free, cloud)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url_resolved or "https://api.opencode.ai/v1"
    
    def is_available(self) -> bool:
        return True  # OpenCode Zen is always available (free)
    
    def _make_request(self, payload: Dict) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        # OpenCode Zen doesn't require API key
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                data = json.loads(response.read().decode())
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"OpenCode API error {e.code}: {error_body}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": False,
        }
        return self._make_request(payload)
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"OpenCode API error {e.code}: {error_body}")

class GroqProvider(LLMProvider):
    """Groq provider (free tier, cloud)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url_resolved or "https://api.groq.com/openai/v1"
        self.api_key = config.get_api_key()
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def _make_request(self, payload: Dict, stream: bool = False) -> Any:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "mindbridge/1.0"
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                if stream:
                    return response
                data = json.loads(response.read().decode())
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"Groq API error {e.code}: {error_body}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": False,
        }
        return self._make_request(payload)
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }
        response = self._make_request(payload, stream=True)
        try:
            for line in response:
                line = line.decode().strip()
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        content = chunk["choices"][0]["delta"].get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"Groq API error {e.code}: {error_body}")

class OllamaProvider(LLMProvider):
    """Ollama provider (local)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url_resolved or "http://localhost:11434"
    
    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                models = [m["name"] for m in data.get("models", [])]
                return any(self.config.model in m for m in models)
        except Exception:
            return False
    
    def _make_request(self, payload: Dict, stream: bool = False) -> Any:
        url = f"{self.base_url}/api/chat"
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                if stream:
                    return response
                data = json.loads(response.read().decode())
                return data["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            # Try fallback models
            for fallback in self.config.fallback_models:
                if fallback != self.config.model:
                    logger.info(f"Trying fallback model: {fallback}")
                    payload["model"] = fallback
                    try:
                        with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                            data = json.loads(response.read().decode())
                            return data["message"]["content"]
                    except Exception:
                        continue
            raise RuntimeError(f"Ollama API error {e.code}: {error_body}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            },
            "stream": False,
        }
        return self._make_request(payload)
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            },
            "stream": True,
        }
        response = self._make_request(payload, stream=True)
        try:
            for line in response:
                line = line.decode().strip()
                if line:
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"Ollama API error {e.code}: {error_body}")

class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible provider (custom endpoints)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url_resolved or "https://api.openai.com/v1"
        self.api_key = config.get_api_key()
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def _make_request(self, payload: Dict, stream: bool = False) -> Any:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                if stream:
                    return response
                data = json.loads(response.read().decode())
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"OpenAI-compatible API error {e.code}: {error_body}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": False,
        }
        return self._make_request(payload)
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                for line in response:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"API error {e.code}: {error_body}")

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    PROVIDER_CLASSES = {
        "opencode": OpenCodeProvider,
        "groq": GroqProvider,
        "ollama": OllamaProvider,
        "openai_compatible": OpenAICompatibleProvider,
    }
    
    @classmethod
    def create(cls, config: LLMConfig) -> LLMProvider:
        provider_class = cls.PROVIDER_CLASSES.get(config.provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {config.provider_type}")
        return provider_class(config)
    
    @classmethod
    def register(cls, name: str, provider_class: type) -> None:
        cls.PROVIDER_CLASSES[name] = provider_class

class LLMManager:
    """Manages multiple LLM providers with fallback chain."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.providers: Dict[str, LLMProvider] = {}
        self.fallback_chain: List[str] = []
        self.embedding_config = EmbeddingConfig()
        self.ask_config = AskModeConfig()
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Load providers
        providers_config = config.get("llm_providers", {})
        for name, provider_config in providers_config.items():
            if provider_config.get("enabled", True):
                config_obj = LLMConfig(
                    name=name,
                    **provider_config
                )
                provider = LLMProviderFactory.create(config_obj)
                self.providers[name] = provider
        
        # Set fallback chain
        self.fallback_chain = config.get("fallback_chain", ["opencode", "groq", "ollama"])
        
        # Load embedding config
        emb_config = config.get("embeddings", {})
        self.embedding_config = EmbeddingConfig(**emb_config)
        
        # Load ask mode config
        ask_config = config.get("ask_mode", {})
        self.ask_config = AskModeConfig(**ask_config)
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get provider by name."""
        return self.providers.get(name)
    
    def get_best_provider(self) -> Optional[LLMProvider]:
        """Get the best available provider based on fallback chain."""
        for name in self.fallback_chain:
            provider = self.providers.get(name)
            if provider and provider.is_available():
                return provider
        return None
    
    def get_provider_by_name(self, name: str) -> Optional[LLMProvider]:
        """Get specific provider by name."""
        return self.providers.get(name)
    
    def chat_with_fallback(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Try providers in fallback chain until one succeeds."""
        last_error = None
        
        for name in self.fallback_chain:
            provider = self.providers.get(name)
            if not provider or not provider.is_available():
                continue
            try:
                return provider.chat(messages, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {name} failed: {e}")
                last_error = e
                continue
        
        if last_error:
            raise last_error
        raise RuntimeError("No available LLM providers")
    
    def stream_chat_with_fallback(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Stream chat with fallback chain."""
        for name in self.fallback_chain:
            provider = self.providers.get(name)
            if not provider or not provider.is_available():
                continue
            try:
                yield from provider.stream_chat(messages, **kwargs)
                return
            except Exception as e:
                logger.warning(f"Provider {name} failed: {e}")
                continue
        raise RuntimeError("No available LLM providers for streaming")

# Embedding functions
def get_embedding(text: str, config: EmbeddingConfig) -> List[float]:
    """Get embedding for text using configured provider."""
    if config.provider == "ollama":
        url = f"{config.base_url}/api/embeddings"
        payload = {
            "model": config.model,
            "prompt": text[:8000],  # Truncate long texts
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data["embedding"]
    raise ValueError(f"Unsupported embedding provider: {config.provider}")

def get_embeddings_batch(texts: List[str], config: EmbeddingConfig) -> List[List[float]]:
    """Get embeddings for multiple texts."""
    embeddings = []
    for i in range(0, len(texts), config.batch_size):
        batch = texts[i:i + config.batch_size]
        batch_embeddings = []
        for text in batch:
            batch_embeddings.append(get_embedding(text, config))
        embeddings.extend(batch_embeddings)
    return embeddings

def load_llm_config(config_path: str) -> Dict:
    """Load LLM configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_default_config(config_path: str) -> None:
    """Create default configuration file."""
    default_config = {
        "llm_providers": {
            "opencode": {
                "enabled": True,
                "priority": 1,
                "provider_type": "opencode",
                "model": "freemodel",
                "timeout": 60,
                "max_tokens": 4096,
                "temperature": 0.2,
            },
            "groq": {
                "enabled": True,
                "priority": 2,
                "provider_type": "groq",
                "model": "openai/gpt-oss-120b",
                "api_key_env": "GROQ_API_KEY",
                "base_url": "https://api.groq.com/openai/v1",
                "timeout": 60,
                "max_tokens": 4096,
                "temperature": 0.2,
            },
            "ollama": {
                "enabled": True,
                "priority": 3,
                "provider_type": "ollama",
                "model": "llama3.2",
                "base_url": "http://localhost:11434",
                "timeout": 120,
                "max_tokens": 4096,
                "temperature": 0.2,
                "fallback_models": ["phi3:mini", "qwen2.5:7b-instruct"],
            },
            "openai_compatible": {
                "enabled": False,
                "priority": 4,
                "provider_type": "openai_compatible",
                "model": "gpt-3.5-turbo",
                "api_key_env": "OPENAI_API_KEY",
                "base_url": "https://api.openai.com/v1",
                "timeout": 60,
                "max_tokens": 4096,
                "temperature": 0.2,
            },
        },
        "fallback_chain": ["opencode", "groq", "ollama"],
        "embeddings": {
            "provider": "ollama",
            "model": "nomic-embed-text",
            "base_url": "http://localhost:11434",
            "dimensions": 768,
            "batch_size": 32,
        },
        "ask_mode": {
            "default_provider": "auto",
            "max_passages": 12,
            "max_passage_chars": 700,
            "context_window": 4096,
            "temperature": 0.2,
            "fallback_context_windows": [4096, 2048, 1024],
            "citation_format": "[S{num}]",
            "save_briefings": True,
            "briefings_dir": "Briefings",
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

# Backward compatibility functions
def get_llm_manager(config_path: Optional[str] = None) -> LLMManager:
    """Get LLM manager instance."""
    if config_path is None:
        config_path = Path(__file__).parent / "llm_config.yaml"
    return LLMManager(config_path)

def chat_with_llm(messages: List[Dict[str, str]], **kwargs) -> str:
    """Convenience function for chat with fallback."""
    manager = get_llm_manager()
    return manager.chat_with_fallback(messages, **kwargs)

def stream_chat_with_llm(messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
    """Convenience function for streaming chat with fallback."""
    manager = get_llm_manager()
    return manager.stream_chat_with_fallback(messages, **kwargs)