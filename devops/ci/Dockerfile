FROM ghcr.io/centers-health/ci-base:1

ENV POETRY_CACHE_DIR=/cache/poetry

COPY . /app

RUN --mount=type=cache,target=/cache/poetry make install-ci
