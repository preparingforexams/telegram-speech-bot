FROM ghcr.io/blindfoldedsurgery/poetry:2.0.0-pipx-3.11-bullseye

USER root
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
      libasound2 \
      libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists /var/cache/apt/archives
USER app

COPY [ "poetry.toml", "poetry.lock", "pyproject.toml", "./" ]

RUN poetry install --no-interaction --ansi --only=main --no-root

# We don't want the tests
COPY src/bob ./src/bob

RUN poetry install --no-interaction --ansi --only-root

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

ENTRYPOINT [ "tini", "--", "poetry", "run", "python", "-m", "bob" ]
CMD [ "handle-updates" ]
