"""Tarifas de modelos (USD por millón de tokens) y cálculo de costos.

Valores aproximados, editables. Se usan para reportar costos estimados en el dashboard.
"""
from __future__ import annotations
from app.core.config import settings

# (precio_input_por_Mtok, precio_output_por_Mtok) en USD
PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-opus-4-8": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    # OpenAI
    "gpt-4o": (2.5, 10.0),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1": (2.0, 8.0),
}

_DEFAULT = (3.0, 15.0)  # fallback si el modelo no está en la tabla


def cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    p_in, p_out = PRICING.get(model, _DEFAULT)
    return round((tokens_in / 1_000_000) * p_in + (tokens_out / 1_000_000) * p_out, 6)


def cost_clp(usd: float) -> float:
    return round(usd * settings.USD_TO_CLP, 2)
