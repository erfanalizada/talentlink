FROM python:3.11-slim

WORKDIR /app

# Copy shared library first
COPY shared/ /app/shared/

# Copy service-specific files
COPY cv-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY cv-service/ .

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 5003

CMD ["python", "app.py"]
