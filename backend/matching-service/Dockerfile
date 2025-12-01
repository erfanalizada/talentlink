FROM python:3.11-slim

WORKDIR /app

# Copy shared library first
COPY shared/ /app/shared/

# Copy service-specific files
COPY matching-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY matching-service/ .

EXPOSE 5004

CMD ["python", "app.py"]
