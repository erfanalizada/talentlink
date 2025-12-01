FROM python:3.11-slim

WORKDIR /app

# Copy shared library first
COPY shared/ /app/shared/

# Copy service-specific files
COPY job-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY job-service/ .

EXPOSE 5001

CMD ["python", "app.py"]
