#!/bin/bash
# BloodLink Render Startup Script
set -e

echo "🚀 Starting BloodLink..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1 || sleep 5

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "🌐 Starting Gunicorn..."
exec gunicorn bloodlink_project.wsgi:application --log-file - --bind 0.0.0.0:$PORT
