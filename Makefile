.PHONY: up dev build down restart rebuild reset logs logs-web logs-db logs-redis \
        shell shell-db shell-redis migrate makemigrations collectstatic \
        createsuperuser check backup-db restore-db ps stop clean prune \
        prod prod-build

# Default command
.DEFAULT_GOAL := up
LIFEGRAPH_VPS_ENV_FILE ?= deploy/vps/env/.env.lifegraph

# ==============================
# Docker Control
# ==============================

up:
	docker compose up -d

dev:
	docker compose up

build:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

rebuild:
	docker compose down
	docker compose up -d --build

reset:
	docker compose down -v
	docker compose up -d --build


# ==============================
# Logs
# ==============================

logs:
	docker compose logs -f

logs-web:
	docker compose logs -f lifegraph_web

logs-db:
	docker compose logs -f lifegraph_db

logs-redis:
	docker compose logs -f lifegraph_redis


# ==============================
# Container Shell
# ==============================

shell:
	docker compose exec lifegraph_web bash

shell-db:
	docker compose exec lifegraph_db bash

shell-redis:
	docker compose exec lifegraph_redis sh


# ==============================
# Django Management
# ==============================

migrate:
	docker compose exec lifegraph_web python manage.py migrate

makemigrations:
	docker compose exec lifegraph_web python manage.py makemigrations

collectstatic:
	docker compose exec lifegraph_web python manage.py collectstatic --noinput

createsuperuser:
	docker compose exec lifegraph_web python manage.py createsuperuser

check:
	docker compose exec lifegraph_web python manage.py check --deploy


# ==============================
# Database Backup / Restore
# ==============================

backup-db:
	docker compose exec lifegraph_db sh -c 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"' > backup.sql

restore-db:
	cat backup.sql | docker compose exec -T lifegraph_db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'


# ==============================
# Utilities
# ==============================

ps:
	docker compose ps

stop:
	docker compose stop

clean:
	docker system prune -f

prune:
	docker system prune -af


# ==============================
# Production
# ==============================

prod:
	test -f "$(LIFEGRAPH_VPS_ENV_FILE)" || (echo "Missing $(LIFEGRAPH_VPS_ENV_FILE). Copy deploy/vps/env/.env.lifegraph.example and fill it first."; exit 1)
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
	LIFEGRAPH_VPS_ENV_FILE="$(LIFEGRAPH_VPS_ENV_FILE)" docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build:
	test -f "$(LIFEGRAPH_VPS_ENV_FILE)" || (echo "Missing $(LIFEGRAPH_VPS_ENV_FILE). Copy deploy/vps/env/.env.lifegraph.example and fill it first."; exit 1)
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
	LIFEGRAPH_VPS_ENV_FILE="$(LIFEGRAPH_VPS_ENV_FILE)" docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
