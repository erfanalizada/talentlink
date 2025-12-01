FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../shared /app/shared
COPY . .

RUN mkdir -p /app/uploads

EXPOSE 5003

CMD ["python", "app.py"]
