FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (including optional LLM support)
RUN uv pip install --system -e ".[dev,llm]"

# Copy application code
COPY . .

CMD ["python", "-m", "bot.bot"]
