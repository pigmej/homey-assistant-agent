FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv && \
    uv sync --frozen

COPY . ./

RUN uv run python main.py download-files

ENV PYTHONPATH=/app

CMD ["uv", "run", "python", "main.py", "start", "--log-level", "debug"]
