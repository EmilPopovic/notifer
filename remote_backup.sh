#!/bin/bash

SERVICE_NAME="notifer"
BACKUP_DIR="db_backups"
RCLONE_REMOTE="b2crypt:homeserver-backup/$SERVICE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    error "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# Find the most recent backup file
LATEST_BACKUP=$(ls -1 "$BACKUP_DIR"/db_????-??-??_??-??-??.dump 2>/dev/null | sort -r | head -n1)

if [ -z "$LATEST_BACKUP" ]; then
    error "No backup files found in $BACKUP_DIR/"
    exit 1
fi

log "Found latest backup: $LATEST_BACKUP"

# Extract just the filename for remote storage
BACKUP_FILENAME=$(basename "$LATEST_BACKUP")

# Upload to remote
log "Uploading backup to remote storage..."
rclone copy "$LATEST_BACKUP" "$RCLONE_REMOTE/" --progress

if [ $? -eq 0 ]; then
    log "Backup successfully uploaded to $RCLONE_REMOTE/$BACKUP_FILENAME"
else
    error "Failed to upload backup to remote storage!"
    exit 1
fi

# Clean up old remote backups (keep last 14 days)
log "Cleaning up old remote backups (keeping last 14 days)..."
rclone delete "$RCLONE_REMOTE/" --min-age 14d

# Optional: Show what's currently stored remotely
log "Current remote backups:"
rclone ls "$RCLONE_REMOTE/" --human-readable

log "$SERVICE_NAME backup completed successfully!"
