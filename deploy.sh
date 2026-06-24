#!/usr/bin/env bash
# Deploy de ABAP Factory AI en el VPS (Docker + Caddy con TLS automático).
# Uso:  bash deploy.sh
set -euo pipefail

cd "$(dirname "$0")"

echo "==> ABAP Factory AI — deploy de producción"

if [ ! -f .env.prod ]; then
  echo "ERROR: falta .env.prod. Copia .env.prod.example y complétalo:"
  echo "       cp .env.prod.example .env.prod && nano .env.prod"
  exit 1
fi

if ! grep -q "tudominio" Caddyfile; then
  echo "==> Caddyfile ya tiene dominio configurado."
else
  echo "AVISO: edita el dominio en Caddyfile antes de exponer (abapfactory.tudominio.cl)."
fi

echo "==> Construyendo e iniciando contenedores..."
docker compose -f docker-compose.prod.yml up -d --build

echo "==> Esperando a la base de datos..."
sleep 8

echo "==> Sembrando datos demo (idempotente)..."
docker compose -f docker-compose.prod.yml exec -T backend python seed.py || true

echo "==> Estado:"
docker compose -f docker-compose.prod.yml ps

echo "==> Listo. Revisa: https://<tu-dominio>/health"
