FROM python:3.13-slim

# System packages needed for cffi, pycairo, pygobject, psutil, and lxml builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    gobject-introspection \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency manifests first
COPY pyproject.toml ./

# Force a version of PyGObject compatible with the libraries in Debian Bookworm
RUN pip install --no-cache-dir "pygobject<=3.50.0"

# Install the rest of the dependencies
RUN pip install --no-cache-dir ".[tests]" || pip install --no-cache-dir .

# Pass --build-arg CACHEBUST=$(date +%s) to force this layer to rebuild
ARG CACHEBUST=1
COPY src/ ./src/
COPY locale/ ./locale/

RUN mkdir -p events tmp
EXPOSE 8080

CMD ["python", "src/server_cloud.py", "--port", "8080"]