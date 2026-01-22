FROM python:3.12.7-slim-bookworm AS builder

# Install uv
RUN pip install uv

WORKDIR /app

# Copy the entire project
COPY . .

# Install dependencies into a virtual environment
RUN uv venv --python 3.12.7 && \
    uv sync --no-dev

# Runtime stage
FROM python:3.12.7-slim-bookworm AS runtime

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy the application code
COPY . /app

# Copy .env files if they exist
COPY .env* /app/

WORKDIR /app

# Expose the application port
EXPOSE 8080

# Command to run the application
ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "main:app"]
