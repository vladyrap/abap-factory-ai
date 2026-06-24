"""Recuperación RAG ligera por cliente — SIN dependencias externas ni embeddings.

Usa scoring por solapamiento de términos (bag-of-words) entre la consulta y cada
fragmento. Suficiente y robusto para inyectar contexto del cliente en los prompts.
"""
from __future__ import annotations
import re
from sqlalchemy.orm import Session
from app.models.client_knowledge import ClientKnowledge

# Stopwords mínimas (español + ABAP comunes) para no puntuar ruido
_STOP = {
    "de", "la", "el", "los", "las", "un", "una", "y", "o", "que", "en", "para", "con",
    "por", "del", "al", "se", "su", "como", "the", "a", "of", "to", "and", "data",
}


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9_]+", (text or "").lower()) if len(t) > 2 and t not in _STOP}


def retrieve(db: Session, client_id: int | None, query: str, top_k: int = 4, max_chars: int = 2500) -> str:
    """Devuelve un bloque de texto con los fragmentos más relevantes del cliente.

    Cadena vacía si no hay cliente o no hay conocimiento relevante.
    """
    if not client_id:
        return ""
    rows = db.query(ClientKnowledge).filter(ClientKnowledge.client_id == client_id).all()
    if not rows:
        return ""

    q = _tokens(query)
    scored = []
    for r in rows:
        doc = _tokens(f"{r.title} {r.content}")
        overlap = len(q & doc)
        if overlap > 0:
            scored.append((overlap, r))
    if not scored:
        return ""

    scored.sort(key=lambda x: x[0], reverse=True)
    chunks, total = [], 0
    for _, r in scored[:top_k]:
        piece = f"## {r.title} ({r.kind})\n{r.content.strip()}"
        if total + len(piece) > max_chars:
            piece = piece[: max(0, max_chars - total)]
        chunks.append(piece)
        total += len(piece)
        if total >= max_chars:
            break

    return (
        "# Contexto del cliente (referencia — reutiliza estos objetos/estándares cuando aplique)\n"
        + "\n\n".join(chunks)
    )
