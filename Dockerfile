# Use an official Python runtime as a parent image
FROM python:3.11-slim
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
# Set work directory
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# Copy requirements file
COPY requirements.txt /app/
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy project files
COPY . /app/
# Create data directory for SQLite DB
RUN mkdir -p /app/data
# Expose port
EXPOSE 5000
# Initialize/migrate DB and then start Gunicorn
CMD ["sh", "-c", "python -c 'from db import init_db, migrate_db; init_db(); migrate_db()' && gunicorn --bind 0.0.0.0:${PORT} --workers 1 app:app"]
