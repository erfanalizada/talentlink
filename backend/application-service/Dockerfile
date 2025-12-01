FROM python:3.11-slim

WORKDIR /app

# Copy shared library first
COPY shared/ /app/shared/

# Copy service-specific files
COPY application-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY application-service/ .

EXPOSE 5002

CMD ["python", "app.py"]
