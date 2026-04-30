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

# Run migrations with error handling
echo "🔄 Running database migrations..."
if python manage.py migrate --noinput; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed, trying to reset..."
    python manage.py migrate --fake-initial --noinput || true
fi

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create initial data if needed
echo "🔧 Setting up initial data..."
python manage.py init_blood_stocks --noinput || echo "Blood stocks already initialized"
python manage.py setup_initial_data --noinput || echo "Initial data already set up"

# Start the application
echo "🌐 Starting Gunicorn on port $PORT..."
exec gunicorn bloodlink_project.wsgi:application --log-file - --bind 0.0.0.0:$PORT --workers 3
