# syntax=docker/dockerfile:1

# ---- Builder: resolve and install dependencies with uv ----
FROM python:3.13-slim-bookworm AS builder

# Bring in the uv binary.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies first (without the project) for better layer caching.
# Only the main deps + the prod group (the WSGI server); dev tooling is excluded.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-default-groups --group prod

# Add the application code and install the project itself.
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-default-groups --group prod

# ---- Runtime: slim image with just the virtualenv ----
FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

COPY --from=builder /app /app

# Use the virtualenv created by uv.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 80
CMD ["gunicorn", "--config", "docker_files/gunicorn_conf.py", "--bind", "0.0.0.0:80", "burn.wsgi:application"]
