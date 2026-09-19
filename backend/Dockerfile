FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/backend
WORKDIR /app
COPY backend/requirements.txt backend/requirements.lock ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt -c backend/requirements.lock \
    && useradd --create-home --uid 10001 clausegraph
COPY backend ./backend
COPY fixtures ./fixtures
COPY migrations ./migrations
COPY scripts ./scripts
COPY pyproject.toml ./
RUN mkdir -p /app/.data/documents && chown -R clausegraph:clausegraph /app/.data
USER clausegraph
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "clausegraph.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
