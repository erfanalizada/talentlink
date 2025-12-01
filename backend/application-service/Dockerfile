FROM python:3.11-slim

WORKDIR /app

# Copy service-specific files
COPY application-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY shared /app/shared

# Copy service code
COPY application-service /app

EXPOSE 5002

CMD ["python", "app.py"]
