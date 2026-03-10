#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

STAMP=$(date +%Y%m%d_%H%M%S)
OUT="/sdcard/Download/fontanero_full_backup_${STAMP}.tar.gz"

echo "Comprimiendo todo (incluyendo venv) a: $OUT"
tar -czf "$OUT" .

echo "Calculando checksum..."
md5sum "$OUT" > "${OUT}.md5"

echo "Tamaño del backup:"
ls -lh "$OUT"

echo "Backup completo creado en: $OUT"
