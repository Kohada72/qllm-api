FROM python:3.12-slim

ENV POETRY_VERSION=1.8.2
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" --break-system-packages

WORKDIR /app

RUN poetry config virtualenvs.create false

COPY gui/pyproject.toml gui/poetry.lock* ./

RUN poetry install --no-root --only main

COPY gui/ .

ENV PORT_NUMBER=8501
ENTRYPOINT ["poetry", "run", "streamlit", "run", "main.py", "--server.address", "0.0.0.0"]