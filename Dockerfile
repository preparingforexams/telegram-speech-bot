FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libssl-dev libasound2 && apt-get clean

RUN pip install poetry==1.4.2 --no-cache
RUN poetry config virtualenvs.create false

COPY [ "poetry.toml", "poetry.lock", "pyproject.toml", "./" ]

# We don't want the tests
COPY src/bob ./src/bob

RUN poetry install --no-dev

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

ENTRYPOINT [ "python", "-m", "bob" ]
CMD [ "handle-updates" ]
