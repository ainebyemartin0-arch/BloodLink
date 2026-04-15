#!/bin/bash

# BloodLink Deployment Script
# Usage: ./deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
echo "🚀 Deploying BloodLink to $ENVIRONMENT environment..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY is required"
    exit 1
fi

if [ "$ENVIRONMENT" = "production" ]; then
    echo "🏭 Production deployment mode"
    
    # Production checks
    if [ -z "$DB_PASSWORD" ]; then
        echo "❌ DB_PASSWORD is required for production"
        exit 1
    fi
    
    if [ -z "$AT_API_KEY" ]; then
        echo "❌ AT_API_KEY is required for production"
        exit 1
    fi
    
    # Deploy with Docker Compose
    echo "🐳 Starting production containers..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
    
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo "🧪 Staging deployment mode"
    docker-compose up --build -d
    
else
    echo "❌ Unknown environment: $ENVIRONMENT"
    echo "Usage: ./deploy.sh [production|staging]"
    exit 1
fi

echo "✅ Deployment completed!"
echo "🌐 Application is running at: http://localhost:8000"
