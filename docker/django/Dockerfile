FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev postgresql-client fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements /tmp/requirements

RUN pip install --upgrade pip

COPY docker/django/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


FROM base AS dev
RUN pip install -r /tmp/requirements/dev.txt
COPY src /app
ENTRYPOINT ["entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM base AS prod
RUN pip install -r /tmp/requirements/prod.txt
COPY src /app
COPY docker/django/gunicorn.conf.py /app/gunicorn.conf.py
ARG GIT_COMMIT=""
RUN echo "${GIT_COMMIT}" > /app/.git_commit
RUN addgroup --system --gid 10001 app \
    && adduser --system --uid 10001 --ingroup app appuser \
    && mkdir -p /app/media /app/staticfiles /app/backups/manual /app/backups/scheduled-db /app/backups/scheduled-media \
    && chown -R appuser:app /app
USER appuser
ENTRYPOINT ["entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--config", "/app/gunicorn.conf.py"]
