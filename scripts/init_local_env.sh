#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ -f .env ]]; then
  echo ".env already exists, skip."
  exit 0
fi

cat > .env <<'EOF'
DJANGO_SECRET_KEY=unsafe-dev-key
DJANGO_DEBUG=true
POSTGRES_DB=lifegraph_db
POSTGRES_USER=lifegraph_user
POSTGRES_PASSWORD=lifegraph_password
DB_FORWARD_PORT=25433
WEB_FORWARD_PORT=28000
USE_REDIS_CACHE=true
EOF
echo "Created LifeGraph .env"
