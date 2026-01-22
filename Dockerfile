FROM python:3.12.7-slim-bookworm AS builder

# Install uv and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

WORKDIR /app

# Copy dependency files and README first for better caching and validation
COPY pyproject.toml uv.lock README.md ./

# Install dependencies into a virtual environment
# We use --extra-index-url to prefer CPU-only torch wheels and reduce image size
# We use --no-install-project to skip installing the project itself (better caching)
RUN uv venv --python 3.12.7 && \
    uv sync --no-dev --no-install-project --extra-index-url https://download.pytorch.org/whl/cpu

# Runtime stage
FROM python:3.12.7-slim-bookworm AS runtime

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy the application code
COPY . /app

# Expose the application port
EXPOSE 8080

# Command to run the application
ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "main:app"]
