# tengo un problema con Open requiere unas librerías que no estan en alpine, usaré slim-bookworm la ultima versión peso 489 MB

FROM python:3.12.7-slim-bookworm AS builder

RUN pip install uv

WORKDIR /app

# Copy the entire project first, including local dependencies that may be need compiled
COPY . .

# Install dependencies
RUN uv venv --python 3.12.7 && \
    uv sync --no-dev

# Runtime stage
# Se asume que /.venv existe en la imagen anterior en el path /app/.venv, tiene las dependencias instaladas. 
FROM python:3.12.7-slim-bookworm AS runtime

# sobreescribimos el path para que exista el binario de uvicorn si no creo que puedo hacer esta linea entry point /app/.venv/uvicorn
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv

COPY . /app 
# NEXT line is to copy optionaly if exists .env files to the container
COPY .env* /app/ 


WORKDIR /app

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "app.main:app"]
