FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy service files
COPY requirements.txt .
COPY . .

# Copy shared code
COPY --from=shared . ./shared

# Install deps
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir ./shared

RUN useradd -m appuser
USER appuser

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "3", "app:app"]
