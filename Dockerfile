FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && \
    uv sync --frozen

COPY agent_tts_stt_g.py ./

RUN uv run python agent_tts_stt_g.py download-files

ENV PYTHONPATH=/app

CMD ["uv", "run", "python", "agent_tts_stt_g.py", "start", "--log-level", "debug"]
