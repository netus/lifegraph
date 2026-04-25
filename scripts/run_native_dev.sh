#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "Native (non-Docker) dev mode has been retired."
echo "Starting Docker dev stack instead..."

if [[ ! -f .env ]]; then
  bash scripts/init_local_env.sh
fi

docker compose up -d --build lifegraph_db lifegraph_redis lifegraph_web
docker compose logs -f lifegraph_web
