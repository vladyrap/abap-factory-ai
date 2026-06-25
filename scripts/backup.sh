#!/usr/bin/env bash
# Backup de la base de datos PostgreSQL (producción, vía Docker).
# Genera un dump comprimido con fecha y rota los antiguos.
# Uso:   bash scripts/backup.sh
# Cron:  0 3 * * *  cd /opt/abap-factory-ai && bash scripts/backup.sh >> backups/backup.log 2>&1
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE="docker compose -f docker-compose.prod.yml"
BACKUP_DIR="./backups"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

# Lee credenciales desde .env.prod (con valores por defecto)
POSTGRES_USER="$(grep -E '^POSTGRES_USER=' .env.prod 2>/dev/null | cut -d= -f2 || echo abap)"
POSTGRES_DB="$(grep -E '^POSTGRES_DB=' .env.prod 2>/dev/null | cut -d= -f2 || echo abap_factory)"

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT="$BACKUP_DIR/${POSTGRES_DB}_${STAMP}.sql.gz"

echo "==> Respaldando $POSTGRES_DB -> $OUT"
$COMPOSE exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$OUT"

# Verifica que el dump no esté vacío
if [ ! -s "$OUT" ]; then
  echo "ERROR: el backup quedó vacío. Revisa que el contenedor 'db' esté arriba." >&2
  rm -f "$OUT"
  exit 1
fi

echo "==> Backup OK ($(du -h "$OUT" | cut -f1))"
echo "==> Rotando backups con más de ${RETENTION_DAYS} días"
find "$BACKUP_DIR" -name "${POSTGRES_DB}_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete
echo "==> Listo. Backups actuales:"
ls -1t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | head -5
