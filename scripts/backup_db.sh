#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/home/filla_saputro/zuzu-bot/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/zuzudb_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "Starting automated database backup for Zuzu Match Bot..."
pg_dump -h 127.0.0.1 -U zuzu -d zuzudb | gzip > "${BACKUP_FILE}"

echo "Backup created successfully at ${BACKUP_FILE}"

# Delete backups older than 7 days
find "${BACKUP_DIR}" -name "zuzudb_*.sql.gz" -mtime +7 -delete
echo "Old backups cleaned up."
