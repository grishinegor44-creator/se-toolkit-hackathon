FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for layer caching
COPY pyproject.toml ./

# Install dependencies (no editable install — avoids hatchling package-discovery issues)
RUN uv pip install --system \
    "aiogram>=3.10.0" \
    "httpx>=0.27.0" \
    "pydantic>=2.0.0" \
    "pydantic-settings>=2.0.0" \
    "python-dotenv>=1.0.0" \
    "openai>=1.30.0" \
    "pytest>=8.0.0" \
    "pytest-asyncio>=0.23.0" \
    "pytest-mock>=3.12.0"

# Copy application code into /app/bot/ so that
# "from bot.config import ..." imports work correctly
RUN mkdir -p /app/bot
COPY . /app/bot/

# Run as a proper Python package module
CMD ["python", "-m", "bot.bot"]
