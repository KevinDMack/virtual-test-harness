FROM python:3.12-slim

LABEL org.opencontainers.image.source=https://github.com/KevinDMack/virtual-test-harness

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Create the /logs directory and grant write access to the non-root user.
# The directory is declared as a VOLUME so it can be bind-mounted or backed
# by a Kubernetes PV/emptyDir, making logs accessible to Arc and monitoring
# services (e.g. Azure Monitor Agent, Fluent Bit).
RUN mkdir -p /logs && chown nobody:nogroup /logs

# Default mount points for config, inbox, and logs directories.
# Override at runtime with -v flags or Kubernetes volume mounts.
VOLUME ["/app/config", "/app/inbox", "/logs"]

ENV APP_BASE_DIR=/app \
    CONFIG_PATH=/app/config/config.json \
    INBOX_DIR=/app/inbox \
    LOG_DIR=/logs

USER nobody

ENTRYPOINT ["python", "app.py"]
