FROM python:3.11-slim

WORKDIR /app

# Copy service-specific files
COPY cv-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY shared ./shared

# Copy service code
COPY cv-service/. .

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 5003

CMD ["python", "app.py"]
