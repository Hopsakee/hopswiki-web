FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN --mount=type=cache,target=/root/.cache uv sync --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache uv sync
RUN adduser --disabled-password --gecos "" appuser
USER appuser
EXPOSE 8080
CMD ["uv", "run", "main.py"]
