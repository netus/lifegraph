#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
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
fi

docker compose up -d lifegraph_db lifegraph_redis lifegraph_web

docker compose exec -T lifegraph_web python manage.py check
docker compose exec -T lifegraph_web python manage.py test -v 2
docker compose exec -T \
  -e DJANGO_DEBUG=false \
  -e DJANGO_SECRET_KEY='replace-with-long-random-secret-key-for-check-only' \
  -e DJANGO_ALLOWED_HOSTS='example.com' \
  -e DJANGO_CSRF_TRUSTED_ORIGINS='https://example.com' \
  lifegraph_web python manage.py check --deploy --fail-level WARNING

echo "All checks passed."
