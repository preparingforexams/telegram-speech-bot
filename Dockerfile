# renovate: datasource=docker depName=debian versioning=debian
ARG DEBIAN_VERSION="bookworm"

# renovate: datasource=python-version depName=python versioning=python
ARG PYTHON_VERSION="3.13"

# renovate: datasource=pypi depName=uv versioning=semver-coerced
ARG UV_VERSION="0.8.8"

FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-${DEBIAN_VERSION}-slim

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
