# Use platform-aware base image for ARM64 safety
FROM --platform=$BUILDPLATFORM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only dependencies first (better build caching)
COPY requirements.txt .

# Install Python dependencies efficiently
# - No need for GCC unless you compile C extensions
# - Clean cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
