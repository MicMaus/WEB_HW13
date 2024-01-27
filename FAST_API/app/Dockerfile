FROM python:3.10

COPY . .

WORKDIR /app

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


CMD ["poetry", "run", "uvicorn", "main:app", "--host", "localhost", "--port", "8001", "--reload"]
