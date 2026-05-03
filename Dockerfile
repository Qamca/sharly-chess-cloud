FROM python:3.13-slim

# System packages needed for cffi (argon2), psutil, and lxml builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency manifests first for better layer caching
COPY pyproject.toml ./

# Install dependencies (no extras that need GTK/GUI)
RUN pip install --no-cache-dir ".[tests]" || pip install --no-cache-dir .

# Copy the rest of the source
COPY src/ ./src/
COPY locale/ ./locale/

# Persistent data directories — populated at runtime via volumes
RUN mkdir -p events tmp

# Expose the web server port
EXPOSE 8080

CMD ["python", "src/server_cloud.py", "--port", "8080"]
