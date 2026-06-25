"""Rate limiter en memoria (ventana deslizante) — sin dependencias externas.

Suficiente para proteger el login de fuerza bruta. Es por-proceso (si escalas a varios
workers, cada uno lleva su cuenta); para límites estrictos multi-nodo, migrar a Redis.
"""
from __future__ import annotations
import threading
import time
from collections import defaultdict, deque

_lock = threading.Lock()
_hits: dict[str, deque] = defaultdict(deque)


def check_and_hit(key: str, max_hits: int, window_sec: int) -> bool:
    """Registra un intento. Devuelve False si se superó el límite en la ventana."""
    now = time.time()
    with _lock:
        dq = _hits[key]
        while dq and now - dq[0] > window_sec:
            dq.popleft()
        if len(dq) >= max_hits:
            return False
        dq.append(now)
        return True


def reset(key: str) -> None:
    with _lock:
        _hits.pop(key, None)
