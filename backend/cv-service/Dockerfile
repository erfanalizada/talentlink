FROM python:3.11-slim

WORKDIR /app

# Copy service-specific files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 5003

CMD ["python", "app.py"]
