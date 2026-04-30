#!/bin/bash
# BloodLink Render Startup Script
set -e

echo "🚀 Starting BloodLink..."

# Check if we're on Render
if [ "$RENDER" = "true" ]; then
    echo "🌐 Running on Render.com"
    
    # Check if DATABASE_URL is set
    if [ -z "$DATABASE_URL" ]; then
        echo "❌ DATABASE_URL not set, using SQLite fallback"
        export DATABASE_URL="sqlite:///db.sqlite3"
    fi
    
    echo "🔗 Database URL: ${DATABASE_URL:0:20}..."
    
    # Wait for database to be ready (only for PostgreSQL)
    if [[ $DATABASE_URL == postgresql* ]]; then
        echo "⏳ Waiting for PostgreSQL database..."
        for i in {1..30}; do
            if python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; then
                echo "✅ Database is ready!"
                break
            fi
            echo "⏳ Waiting for database... ($i/30)"
            sleep 2
        done
    fi
else
    echo "💻 Running locally"
fi

# Run emergency fix and diagnostics
echo "� Running emergency diagnostics and fix..."
python emergency_fix.py

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start the application
echo "🌐 Starting Gunicorn on port $PORT..."
exec gunicorn bloodlink_project.wsgi:application --log-file - --bind 0.0.0.0:$PORT --workers 3
