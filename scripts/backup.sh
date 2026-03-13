#!/bin/bash
echo "💾 Creating backup..."

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
docker exec zero2hacker-ctf-postgres-1 pg_dump -U ctf_user zero2hacker_ctf > "$BACKUP_DIR/database.sql"

# Backup uploaded files
tar -czf "$BACKUP_DIR/uploads.tar.gz" uploads/

# Backup configuration
cp -r backend/.env frontend/.env docker/ "$BACKUP_DIR/"

echo "✅ Backup created: $BACKUP_DIR"
