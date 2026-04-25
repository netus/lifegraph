# LifeGraph

**English** · [简体中文](README.zh-CN.md)

Turn life experiences into structured nodes — *when / where / who / what* — and weave them into a graph.

> One node = one real experience.
> Node structure = three coordinates (time / place / participants) + content.
> Essence: turn life into recordable, searchable, connectable data.

Full product definition: [`docs/product.md`](docs/product.md) (Chinese).

---

## Current Stage

Stage 1 — single-user node system:

- Minimal input: write a node in one sentence
- Timeline as the main view (front end)
- Node / participant management via Django Admin (Unfold theme)
- i18n: zh-hans / en
- Roadmap: AI auto-structuring → multi-user nodes → relationship graph visualization

---

## Tech Stack

| Layer | Choice |
| --- | --- |
| Web | Django 5.x + Gunicorn |
| DB | PostgreSQL 17 |
| Cache / Session | Redis 7 |
| Admin | django-unfold |
| Scheduler | django-apscheduler |
| Reverse proxy | Caddy 2.8 (production) |
| Orchestration | Docker Compose (base + override + prod, three files) |

---

## Layout

```
.
├── docker-compose.yml              # base service definitions
├── docker-compose.override.yml     # local-dev overrides (auto-loaded)
├── docker-compose.prod.yml         # production overrides
├── Makefile                        # one-liner ops commands
├── docker/django/                  # Dockerfile / entrypoint / gunicorn
├── deploy/vps/                     # Caddyfile + production env example
├── requirements/                   # base / dev / prod dependency sets
├── scripts/                        # local bootstrap & self-check scripts
└── src/
    ├── config/                     # Django settings / urls / wsgi / asgi
    ├── core/                       # middleware, Telegram, Turnstile, upload validators
    ├── apps/lifegraph/             # business models & views
    ├── templates/                  # front-end + admin templates
    ├── static/                     # hand-written static assets
    └── locale/                     # i18n translations
```

---

## Quick Start (local dev)

Prerequisites: Docker Desktop.

```bash
# 1. Bootstrap a local .env (placeholders only, ready to run)
bash scripts/init_local_env.sh

# 2. Bring up services (db + redis + web)
make up

# 3. Run migrations
make migrate

# 4. Create a superuser
make createsuperuser
```

Visit:

- Front timeline: <http://localhost:28000/>
- Admin: <http://localhost:28000/admin/> (path controlled by `DJANGO_ADMIN_URL`)

Common commands:

```bash
make logs          # tail all logs
make logs-web      # only Django
make shell         # shell into web container
make shell-db      # shell into Postgres
make down          # stop services
make reset         # wipe volumes & rebuild
make check         # Django check --deploy
```

---

## Production Deployment

Production stack uses `docker-compose.yml + docker-compose.prod.yml`, with Caddy fronting Django.

### 1. Prepare the VPS env file

```bash
cp deploy/vps/env/.env.lifegraph.example deploy/vps/env/.env.lifegraph
# Fill in real SECRET_KEY / DB password / domain / ADMIN_URL / etc.
```

Required fields:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Long random string, **mandatory** |
| `DJANGO_DEBUG` | `false` in production |
| `DJANGO_ALLOWED_HOSTS` | Your domain, comma-separated |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://example.com` form |
| `POSTGRES_PASSWORD` | Strong password |
| `APP_DOMAIN` | Domain Caddy will serve |
| `DJANGO_ADMIN_URL` | Custom admin path; avoid the default `/admin/` |

### 2. TLS certificates

By default the Caddyfile reads Cloudflare Origin certs from `/etc/lifegraph/certs/`:

```
/etc/lifegraph/certs/cf-origin.pem
/etc/lifegraph/certs/cf-origin.key
```

Not using Cloudflare? Edit `deploy/vps/caddy/Caddyfile` and let Caddy auto-issue Let's Encrypt certs.

### 3. One-shot deploy

```bash
make prod-build
```

This brings the old stack down, rebuilds images, and restarts db / redis / web / proxy.

If `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` are set, `entrypoint.sh` posts a deploy success notification to Telegram.

---

## Security Features

`src/core/middleware.py` ships several middlewares, enabled by default in production:

- `TurnstileAdminLoginMiddleware` — Cloudflare Turnstile on admin login
- `SessionTimeoutMiddleware` — session timeout enforcement
- `RateLimitMiddleware` — per-endpoint rate limiting
- `AdminNoCacheMiddleware` — no-cache for admin pages
- `SecurityHeadersMiddleware` — extra security response headers

The `if not DEBUG` branch in `settings.py` enforces HSTS / Secure cookies / X-Frame-Options / etc.

---

## Backup & Restore

```bash
make backup-db                    # dump to ./backup.sql
make restore-db                   # restore from ./backup.sql
```

In production the `lifegraph_backup_data` volume maps to `/app/backups/` inside the container. Combine with `django-apscheduler` for scheduled backups.

---

## Project Status

This repo is currently **archived**. Future work timeline is undefined — feel free to fork.

---

## License

See [LICENSE](LICENSE).
