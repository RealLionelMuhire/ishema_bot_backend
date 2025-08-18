#!/bin/bash

# Set default port if not provided
PORT=${PORT:-8000}

echo "Starting server on port $PORT"

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn
exec gunicorn --bind 0.0.0.0:$PORT ml_chatbot.wsgi:application
