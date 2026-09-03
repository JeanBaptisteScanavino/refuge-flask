# Base stage with common dependencies
FROM python:3.12-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY wsgi.py .

# Development stage
FROM base AS development

ENV FLASK_ENV=development
ENV FLASK_DEBUG=True
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]

# Production stage
FROM base AS production

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
