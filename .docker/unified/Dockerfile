FROM python:3.12-slim AS builder

WORKDIR /enquiry-automation-service
ENV POETRY_HOME="/opt/poetry"
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install --upgrade pip && \
    $POETRY_HOME/bin/pip install poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-interaction --no-ansi --no-root


FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-calc \
    fonts-liberation \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /enquiry-automation-service

ENV POETRY_HOME="/opt/poetry"
COPY --from=builder ${POETRY_HOME} ${POETRY_HOME}
COPY --from=builder /enquiry-automation-service/pyproject.toml /enquiry-automation-service/poetry.lock ./
COPY --from=builder /enquiry-automation-service/.venv ./.venv

ENV PATH="${POETRY_HOME}/bin:/enquiry-automation-service/.venv/bin:${PATH}"

COPY ./src ./src
EXPOSE 7778
CMD ["poetry", "run", "python", "src/main.py"]