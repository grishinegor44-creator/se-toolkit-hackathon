FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (no editable install — avoids hatchling package-discovery issues)
RUN uv pip install --system \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "sqlalchemy[asyncio]>=2.0.0" \
    "asyncpg>=0.29.0" \
    "httpx>=0.27.0" \
    "pydantic>=2.0.0" \
    "pydantic-settings>=2.0.0" \
    "python-dotenv>=1.0.0" \
    "pytest>=8.0.0" \
    "pytest-asyncio>=0.23.0" \
    "pytest-mock>=3.12.0" \
    "respx>=0.21.0"

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
