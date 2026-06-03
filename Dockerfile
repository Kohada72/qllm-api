FROM pytorch/pytorch:2.12.0-cuda13.2-cudnn9-devel

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring \
    PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml ./

RUN sed -i '/torch/d' pyproject.toml

RUN poetry install --no-root --no-interaction --no-cache

COPY . .

ENTRYPOINT ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]