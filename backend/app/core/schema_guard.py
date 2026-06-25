"""Auto-migración aditiva de esquema — robustez sin recrear la BD.

`create_all` crea tablas faltantes pero NUNCA agrega columnas nuevas a tablas
existentes. Esto, en una BD ya poblada, provoca errores "no such column".

`ensure_columns` compara los modelos con la BD real y agrega (ALTER TABLE ADD COLUMN)
las columnas que falten, rellenando el valor por defecto del modelo. Funciona en
PostgreSQL y SQLite para cambios ADITIVOS (no renombra ni borra; para eso, Alembic).
"""
from __future__ import annotations
import logging
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)


def ensure_columns(engine=None, metadata=None) -> list[str]:
    """Agrega columnas faltantes. Devuelve la lista 'tabla.columna' agregadas."""
    if engine is None or metadata is None:
        from app.core.database import engine as _e, Base
        import app.models  # noqa: F401 — puebla Base.metadata
        engine = engine or _e
        metadata = metadata or Base.metadata

    insp = inspect(engine)
    existing_tables = set(insp.get_table_names())
    added: list[str] = []

    for table_name, table in metadata.tables.items():
        if table_name not in existing_tables:
            continue  # tabla nueva → la crea create_all
        db_cols = {c["name"] for c in insp.get_columns(table_name)}
        for col in table.columns:
            if col.name in db_cols:
                continue
            try:
                coltype = col.type.compile(dialect=engine.dialect)
                with engine.begin() as conn:
                    conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{col.name}" {coltype}'))
                    # backfill del valor por defecto del modelo (si es escalar)
                    default = getattr(col.default, "arg", None) if col.default is not None else None
                    if default is not None and not callable(default):
                        conn.execute(
                            text(f'UPDATE "{table_name}" SET "{col.name}" = :v WHERE "{col.name}" IS NULL'),
                            {"v": default},
                        )
                added.append(f"{table_name}.{col.name}")
                logger.info("schema_guard.added_column %s.%s", table_name, col.name)
            except Exception:  # noqa: BLE001 — no abortar el arranque por una columna
                logger.exception("schema_guard.add_failed %s.%s", table_name, col.name)
    if added:
        logger.info("schema_guard.summary added=%s", added)
    return added
