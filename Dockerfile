FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Default mount points for config and inbox directories.
# Override at runtime with -v flags or Kubernetes volume mounts.
VOLUME ["/app/config", "/app/inbox"]

ENV APP_BASE_DIR=/app \
    CONFIG_PATH=/app/config/config.json \
    INBOX_DIR=/app/inbox

USER nobody

ENTRYPOINT ["python", "app.py"]
