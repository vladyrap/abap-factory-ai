#!/usr/bin/env bash
# Restaura un backup de la base de datos. ¡SOBREESCRIBE los datos actuales!
# Uso:   bash scripts/restore.sh backups/abap_factory_20260625_030000.sql.gz
set -euo pipefail

cd "$(dirname "$0")/.."

DUMP="${1:-}"
if [ -z "$DUMP" ] || [ ! -f "$DUMP" ]; then
  echo "Uso: bash scripts/restore.sh <archivo.sql.gz>" >&2
  echo "Backups disponibles:" >&2
  ls -1t ./backups/*.sql.gz 2>/dev/null || echo "  (ninguno)" >&2
  exit 1
fi

COMPOSE="docker compose -f docker-compose.prod.yml"
POSTGRES_USER="$(grep -E '^POSTGRES_USER=' .env.prod 2>/dev/null | cut -d= -f2 || echo abap)"
POSTGRES_DB="$(grep -E '^POSTGRES_DB=' .env.prod 2>/dev/null | cut -d= -f2 || echo abap_factory)"

read -r -p "Esto SOBREESCRIBE la BD '$POSTGRES_DB' con $DUMP. ¿Continuar? (escribe 'si'): " ok
[ "$ok" = "si" ] || { echo "Cancelado."; exit 1; }

echo "==> Restaurando $DUMP -> $POSTGRES_DB"
gunzip -c "$DUMP" | $COMPOSE exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
echo "==> Restauración completada."
