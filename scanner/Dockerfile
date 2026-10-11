FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-cache
ENV PATH="/app/.venv/bin:$PATH"

COPY . .
CMD ["python", "main.py"]
