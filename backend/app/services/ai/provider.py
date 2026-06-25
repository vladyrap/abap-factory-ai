"""Capa de abstracción de proveedores LLM — conmutable entre Claude y OpenAI.

Cada proveedor implementa `complete()` y devuelve un LLMResult uniforme.
Si la API key del proveedor no está configurada, `is_enabled()` devuelve False y
los servicios responden con un fallback en vez de fallar.
"""
from __future__ import annotations
import time
import logging
from dataclasses import dataclass
from typing import Optional, Callable

from app.core.config import settings

logger = logging.getLogger(__name__)

# Subcadenas de tipos de error que SÍ vale la pena reintentar (transitorios).
_RETRYABLE = ("ratelimit", "timeout", "connection", "overloaded", "serviceunavailable",
              "apiconnection", "internalserver", "502", "503", "504")


def _is_retryable(exc: Exception) -> bool:
    name = (type(exc).__name__ + " " + str(exc)).lower()
    return any(tok in name for tok in _RETRYABLE)


def _with_retries(fn: Callable, label: str):
    """Ejecuta fn con reintentos y backoff exponencial ante errores transitorios."""
    attempts = settings.AI_MAX_RETRIES + 1
    delay = 1.0
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last = exc
            if i < attempts - 1 and _is_retryable(exc):
                logger.warning("ai.retry", extra={"provider": label, "attempt": i + 1, "error": str(exc)[:200]})
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise last


@dataclass
class LLMResult:
    text: str
    tokens_in: int
    tokens_out: int
    model: str
    provider: str
    latency_ms: int


class LLMProvider:
    name: str = "base"

    def is_enabled(self) -> bool:
        raise NotImplementedError

    def complete(
        self,
        system: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4000,
    ) -> LLMResult:
        raise NotImplementedError


class ClaudeProvider(LLMProvider):
    name = "claude"

    def is_enabled(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    def complete(self, system, user_prompt, model=None, temperature=0.2, max_tokens=4000) -> LLMResult:
        import anthropic  # import perezoso: solo si se usa
        model = model or settings.CLAUDE_DEFAULT_MODEL
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY,
                                     timeout=settings.AI_TIMEOUT_SECONDS)
        t0 = time.time()
        resp = _with_retries(lambda: client.messages.create(
            model=model,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": user_prompt}],
        ), label="claude")
        latency = int((time.time() - t0) * 1000)
        text = "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")
        return LLMResult(
            text=text,
            tokens_in=resp.usage.input_tokens,
            tokens_out=resp.usage.output_tokens,
            model=model,
            provider=self.name,
            latency_ms=latency,
        )


class OpenAIProvider(LLMProvider):
    name = "openai"

    def is_enabled(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    def complete(self, system, user_prompt, model=None, temperature=0.2, max_tokens=4000) -> LLMResult:
        from openai import OpenAI  # import perezoso
        model = model or settings.OPENAI_DEFAULT_MODEL
        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.AI_TIMEOUT_SECONDS)
        t0 = time.time()
        resp = _with_retries(lambda: client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
        ), label="openai")
        latency = int((time.time() - t0) * 1000)
        text = resp.choices[0].message.content or ""
        usage = resp.usage
        return LLMResult(
            text=text,
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
            model=model,
            provider=self.name,
            latency_ms=latency,
        )


class GeminiProvider(LLMProvider):
    name = "gemini"

    def is_enabled(self) -> bool:
        return bool(settings.GEMINI_API_KEY)

    def complete(self, system, user_prompt, model=None, temperature=0.2, max_tokens=4000) -> LLMResult:
        from google import genai          # import perezoso
        from google.genai import types as gtypes
        model = model or settings.GEMINI_DEFAULT_MODEL
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        config = gtypes.GenerateContentConfig(
            system_instruction=system, temperature=temperature, max_output_tokens=max_tokens,
        )
        t0 = time.time()
        resp = _with_retries(
            lambda: client.models.generate_content(model=model, contents=user_prompt, config=config),
            label="gemini",
        )
        latency = int((time.time() - t0) * 1000)
        usage = getattr(resp, "usage_metadata", None)
        return LLMResult(
            text=resp.text or "",
            tokens_in=getattr(usage, "prompt_token_count", 0) or 0,
            tokens_out=getattr(usage, "candidates_token_count", 0) or 0,
            model=model, provider=self.name, latency_ms=latency,
        )


_PROVIDERS: dict[str, LLMProvider] = {
    "claude": ClaudeProvider(),
    "openai": OpenAIProvider(),
    "gemini": GeminiProvider(),
}


def get_provider(name: Optional[str] = None) -> LLMProvider:
    """Devuelve el proveedor solicitado, o el DEFAULT_AI_PROVIDER si no se especifica."""
    key = (name or settings.DEFAULT_AI_PROVIDER).lower()
    return _PROVIDERS.get(key, _PROVIDERS["claude"])


def any_enabled() -> bool:
    return any(p.is_enabled() for p in _PROVIDERS.values())
