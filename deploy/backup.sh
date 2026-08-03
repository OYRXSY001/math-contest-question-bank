#!/bin/sh
set -eu

app_root=/srv/cmc-a
backup_root=/var/backups/cmc-a
stamp=$(date +%Y%m%d-%H%M%S)

install -d -m 0700 "$backup_root"
sqlite3 "$app_root/db.sqlite3" ".backup '$backup_root/db-$stamp.sqlite3'"
tar -czf "$backup_root/files-$stamp.tar.gz" -C "$app_root" media data/review data/import
find "$backup_root" -maxdepth 1 -type f \( -name 'db-*.sqlite3' -o -name 'files-*.tar.gz' \) -mtime +14 -delete
