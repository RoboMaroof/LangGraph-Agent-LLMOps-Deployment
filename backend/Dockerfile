FROM python:3.10-slim

# System dependencies for Poetry and optional build tools
RUN apt-get update && apt-get install -y curl build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy pyproject files first for caching layer
COPY pyproject.toml poetry.lock ./

# Install dependencies (no-root for app mode)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy actual application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI app
CMD ["poetry", "run", "python", "app.py"]
