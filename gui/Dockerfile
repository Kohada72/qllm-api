FROM python:3.12-slim

ENV WORKDIR_PATH=/app
ENV POETRY_VERSION=1.8.2
ENV PYTHON_BUF=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR $WORKDIR_PATH

RUN poetry config virtualenvs.create false

COPY gui/pyproject.toml gui/poetry.lock* ./

RUN poetry install --no-root --only main

COPY gui/ .

ENV PORT_NUMBER=8501
CMD ["python", "-m", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]