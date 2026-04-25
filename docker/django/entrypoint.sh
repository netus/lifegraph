#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings}"

if [ -n "${POSTGRES_HOST}" ]; then
  export PGPASSWORD="${POSTGRES_PASSWORD:-}"
  until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; do
    echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
    sleep 1
  done

  # Verify actual DB connectivity beyond port check
  python -c "
import django; django.setup()
from django.db import connection
connection.ensure_connection()
" || { echo "ERROR: Cannot connect to database" >&2; exit 1; }
fi

echo "Running migrations..."
python manage.py migrate --noinput || { echo "ERROR: migrate failed" >&2; exit 1; }

echo "Collecting static files..."
python manage.py collectstatic --noinput || { echo "ERROR: collectstatic failed" >&2; exit 1; }

# Deploy notification via Telegram (skip for cron container)
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ] && echo "$*" | grep -q "gunicorn"; then
  export DEPLOY_COMMIT_INFO="$(cat /app/.git_commit 2>/dev/null || echo '')"
  export DEPLOY_LABEL="${APP_DOMAIN:-LifeGraph}"
  python -c "
import os, html, urllib.request, urllib.parse
label = os.environ.get('DEPLOY_LABEL', 'LifeGraph')
commit = os.environ.get('DEPLOY_COMMIT_INFO', '').strip()
msg = '✅ <b>' + html.escape(label) + ' Deploy Succeeded</b>'
if commit:
    msg += '\nCommit: <code>' + html.escape(commit) + '</code>'
data = urllib.parse.urlencode({
    'chat_id': os.environ['TELEGRAM_CHAT_ID'],
    'text': msg,
    'parse_mode': 'HTML',
}).encode()
url = 'https://api.telegram.org/bot' + os.environ['TELEGRAM_BOT_TOKEN'] + '/sendMessage'
try:
    urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10)
except Exception:
    pass
" 2>/dev/null || true
fi

exec "$@"
