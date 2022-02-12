FROM python:3.9-slim
WORKDIR /inferencedb
STOPSIGNAL SIGINT

# Install wget for readiness probe
RUN apt update && apt install -y wget build-essential librocksdb-dev libsnappy-dev zlib1g-dev libbz2-dev liblz4-dev && rm -rf /var/lib/apt/lists/*

# Install python dependencies with poetry
COPY poetry.lock pyproject.toml ./
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-dev

COPY . .
WORKDIR /inferencedb/src
ENTRYPOINT [ "python", "-m", "inferencedb.app" ]
