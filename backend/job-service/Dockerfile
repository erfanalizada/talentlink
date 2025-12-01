FROM python:3.11-slim

WORKDIR /app

# Copy service files
COPY requirements.txt .
COPY . .

# Copy shared code (passed as: --build-context shared=./backend/shared)
COPY --from=shared . ./shared

# Install deps
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir ./shared

EXPOSE 5000

CMD ["python", "app.py"]
