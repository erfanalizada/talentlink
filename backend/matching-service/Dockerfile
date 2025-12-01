FROM python:3.11-slim

WORKDIR /app

# Copy service-specific files
COPY matching-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY shared ./shared

# Copy service code
COPY matching-service/. .

EXPOSE 5004

CMD ["python", "app.py"]
