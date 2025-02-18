FROM ghcr.io/centers-health/ci-base:1

ENV POETRY_CACHE_DIR=/cache/poetry
COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/cache/poetry poetry install --no-root

COPY . .
