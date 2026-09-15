FROM python:3.12-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY requirements-api.txt .
RUN python -m pip wheel --wheel-dir /wheels -r requirements-api.txt

FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    ARO_WORKFLOW_DB_PATH=/app/data/workflows.sqlite3 \
    ARO_SECURITY_DB_PATH=/app/data/security.sqlite3 \
    ARO_DEAD_LETTER_DB_PATH=/app/data/dead_letters.sqlite3

RUN groupadd --gid 10001 aro \
    && useradd --uid 10001 --gid 10001 --create-home --home-dir /home/aro --shell /usr/sbin/nologin aro

WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements-api.txt .
RUN python -m pip install --no-index --find-links=/wheels -r requirements-api.txt \
    && rm -rf /wheels

COPY src ./src
RUN mkdir -p /app/data \
    && chown -R 10001:10001 /app /home/aro

USER 10001:10001
EXPOSE 8000
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2).read()" || exit 1

CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
