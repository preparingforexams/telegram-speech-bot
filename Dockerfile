FROM ghcr.io/astral-sh/uv:0.6-python3.13-bookworm-slim

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
      libasound2 \
      libssl-dev \
      tini \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN groupadd --system --gid 1000 app
RUN useradd --system --uid 1000 --gid app --create-home --home-dir /app app

USER 1000
WORKDIR /app

COPY [ "uv.lock", "pyproject.toml", "./" ]

RUN uv sync --locked --all-extras --no-dev --no-install-workspace

# We don't want the tests
COPY src/bob ./src/bob

RUN uv sync --locked --all-extras --no-dev --no-editable

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

ENV UV_NO_SYNC=true
ENTRYPOINT [ "tini", "--", "uv", "run", "-m", "bob" ]
CMD [ "handle-updates" ]
