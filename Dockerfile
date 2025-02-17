# Build stage for development environment
FROM python:3.10-slim as dev

WORKDIR /app

# Install development dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install package in development mode
RUN pip install -e .

# Default command for development
CMD ["freed", "validate"]

# Build stage for production environment
FROM python:3.10-slim as prod

WORKDIR /app

# Copy only necessary files
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY LICENSE .
COPY freed_validator freed_validator/

# Install production dependencies and package
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir . && \
    rm -rf /root/.cache/pip

# Create non-root user
RUN useradd -m freed && \
    chown -R freed:freed /app
USER freed

# Expose default FreeD port
EXPOSE 6000/udp

# Health check using version command
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD freed --version || exit 1

# Default command for production
ENTRYPOINT ["freed"]
CMD ["validate", "--ip", "0.0.0.0", "--port", "6000"]

# Usage examples in comments:
# Development with local mount:
#   docker build --target dev -t freed-dev .
#   docker run -v $(pwd):/app -p 6000:6000/udp freed-dev
#
# Production deployment:
#   docker build --target prod -t freed .
#   docker run -p 6000:6000/udp freed
#
# Run specific commands:
#   docker run freed test --network
#   docker run freed simulate circle
#   docker run -v $(pwd):/data freed analyze /data/freed_packets.csv
