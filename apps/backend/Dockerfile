# syntax=docker/dockerfile:1

# Base images are pinned by tag and digest; Dependabot raises both together.
# The uv version stays inside the `uv_build` range in pyproject.toml, so uv
# builds the project with its bundled backend instead of downloading one.
FROM ghcr.io/astral-sh/uv:0.10.7@sha256:edd1fd89f3e5b005814cc8f777610445d7b7e3ed05361f9ddfae67bebfe8456a AS uv

FROM python:3.14.7-slim-trixie@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6 AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app

FROM base AS uv-base
COPY --from=uv /uv /uvx /bin/
# Use the image's Python in every stage so the copied virtual environment stays valid.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Builds a self-contained virtual environment: runtime dependencies plus the
# project installed non-editable, so the runtime stage needs no source tree.
FROM uv-base AS builder
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# Development image: editable install with the dev tools and auto-reload.
# `docker compose watch` syncs source changes into /app.
FROM uv-base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
COPY --chown=app:app . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
# The `app` user has no home directory and the virtual environment stays owned
# by root, so uv caches under /tmp and `uv run` uses the environment as built.
# /app itself is writable for pytest, coverage, and Ruff output.
ENV UV_CACHE_DIR=/tmp/uv-cache \
    UV_NO_SYNC=1
RUN chown app:app /app
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "job_status_found.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "src"]

# Production image and the default build target: the virtual environment only,
# owned by root and run by an unprivileged user.
FROM base AS runtime
# Nothing installs packages at runtime.
RUN pip uninstall --yes pip
COPY --from=builder /app/.venv /app/.venv
# The revisions ship with the image, so `alembic upgrade head` runs where the
# code that needs the schema runs.
COPY alembic.ini ./
COPY migrations ./migrations
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --start-interval=1s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
# Exec form keeps uvicorn as PID 1 so it receives SIGTERM and shuts down gracefully.
CMD ["uvicorn", "job_status_found.main:app", "--host", "0.0.0.0", "--port", "8000"]
