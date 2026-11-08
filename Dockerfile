FROM python:3.13-slim

LABEL org.opencontainers.image.title="ClinicShield" \
      org.opencontainers.image.description="Provisional cyber safety checkup prototype" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip check \
    && groupadd --gid 10001 clinicshield \
    && useradd --uid 10001 --gid 10001 --create-home clinicshield

COPY --chown=10001:10001 app.py LICENSE ./
COPY --chown=10001:10001 clinicshield/ ./clinicshield/
COPY --chown=10001:10001 rules/ ./rules/
COPY --chown=10001:10001 config/ ./config/
COPY --chown=10001:10001 templates/ ./templates/
COPY --chown=10001:10001 samples/lakeview_dental/ ./samples/lakeview_dental/
COPY --chown=10001:10001 samples/southside_counseling/ ./samples/southside_counseling/
COPY --chown=10001:10001 samples/westside_health/ ./samples/westside_health/

USER 10001:10001
EXPOSE 8501
HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=6 \
    CMD ["python", "-c", "import urllib.request; r = urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3); assert r.status == 200 and r.read().strip() == b'ok'"]
ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
