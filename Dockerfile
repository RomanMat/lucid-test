# Stage 1: Build environment with uv (builder stage)
FROM ghcr.io/astral-sh/uv:0.6.9-python3.12-bookworm-slim@sha256:4b5c63875e2380dd3623bd61030cb18e3b31f723dcdcd2828e30968758ca5de2 AS builder

# Enable bytecode compilation and link mode
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy 
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
# Ensure cache and bind mounts for uv syncing of dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
# Copy lock and pyproject files and sync again for a complete build.
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Stage 2: Production image
FROM python:3.12-slim-bookworm AS production

# Copy the entire app built by the uv builder.
COPY --from=builder --chown=app:app /app /app
ADD /app /app

# Ensure the virtual environment's bin directory is in the PATH.
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1 
ENV DATABASE_URL=mysql+pymysql://user:password@mysql/dbname
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

WORKDIR /app

# Expose FastAPI's port
EXPOSE 8000

# Run the application using uvicorn (uvloop is already the default with uv)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
