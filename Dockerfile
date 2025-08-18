# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY=django-insecure-build-key-123

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create static directory
RUN mkdir -p /app/static

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Make start.py executable
RUN chmod +x start.py

# Run the start script which handles PORT environment variable
CMD ["python", "start.py"] 