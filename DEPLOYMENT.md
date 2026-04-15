# 🚀 BloodLink Deployment Guide

## 📋 Overview
BloodLink is a Django-based blood donation management system that can be deployed to production using Docker and Docker Compose.

## 🏗️ Architecture

```
┌─────────────────┐
│   Load Balancer │
└─────────────────┘
        │
┌─────────────────┐
│   Web Server   │  (Django + Gunicorn)
└─────────────────┘
        │
┌─────────────────┐
│   PostgreSQL DB │
└─────────────────┘
```

## 🚀 Quick Deployment

### Prerequisites
- Docker & Docker Compose
- Domain name
- SSL certificate (recommended)
- Africa's Talking API account
- Email service (Gmail, SendGrid, etc.)

### Step 1: Configure Environment
```bash
# Copy production environment template
cp .env.production .env

# Edit with your actual values
nano .env
```

### Step 2: Deploy with Docker Compose
```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh production
```

### Step 3: Verify Deployment
```bash
# Check application status
curl -f http://localhost:8000/ || echo "❌ Application not responding"

# Check database connection
docker-compose exec web python manage.py check --deploy
```

## 🔧 Production Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | ✅ |
| `ALLOWED_HOSTS` | Allowed domains | ✅ |
| `DB_NAME` | Database name | ✅ |
| `DB_USER` | Database user | ✅ |
| `DB_PASSWORD` | Database password | ✅ |
| `AT_USERNAME` | Africa's Talking username | ✅ |
| `AT_API_KEY` | Africa's Talking API key | ✅ |
| `EMAIL_HOST` | SMTP server | ✅ |
| `EMAIL_HOST_USER` | SMTP username | ✅ |
| `EMAIL_HOST_PASSWORD` | SMTP password | ✅ |

### Database Setup
```sql
-- Create database (run once)
CREATE DATABASE bloodlink_db;
CREATE USER bloodlink_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE bloodlink_db TO bloodlink_user;
```

## 🌐 Deployment Options

### Option 1: Docker Compose (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f web
```

### Option 2: Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start with Gunicorn
gunicorn bloodlink_project.wsgi:application --bind 0.0.0.0:8000
```

## 🔒 Security Configuration

### SSL/TLS Setup
```bash
# Using Nginx reverse proxy
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Headers
```python
# Already configured in production.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
```

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8000/health/

# Database health
docker-compose exec db pg_isready -U bloodlink_user -d bloodlink_db

# Container health
docker-compose ps
```

### Logging
```bash
# View application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f db
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy BloodLink
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml up --build -d
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database status
docker-compose exec db pg_isready -U bloodlink_user -d bloodlink_db

# Reset database
docker-compose down -v
docker-compose up -d
```

#### 2. Static Files Not Loading
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Check static file permissions
docker-compose exec web ls -la staticfiles/
```

#### 3. SMS Not Working
```bash
# Test Africa's Talking connection
docker-compose exec web python manage.py shell
>>> from notifications.utils import test_africastalking_connection
>>> test_africastalking_connection()
```

#### 4. Permission Errors
```bash
# Check file permissions
docker-compose exec web ls -la media/

# Fix permissions
docker-compose exec web chown -R www-data:www-data media/
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.prod.yml
services:
  web:
    deploy:
      replicas: 3
    # ... other config
```

### Database Optimization
```sql
-- Add indexes for performance
CREATE INDEX CONCURRENTLY donors_blood_type_idx ON donors(blood_type);
CREATE INDEX CONCURRENTLY donors_location_idx ON donors(location);
CREATE INDEX CONCURRENTLY sms_notifications_sent_at_idx ON sms_notifications(sent_at);
```

## 🔧 Maintenance

### Backups
```bash
# Database backup
docker-compose exec db pg_dump -U bloodlink_user bloodlink_db > backup.sql

# Media backup
docker run --rm -v bloodlink_media:/data -v $(pwd):/backup alpine tar czf backup.tar.gz -C /data .
```

### Updates
```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker-compose exec web python manage.py migrate
```

## 📞 Support

### Monitoring Tools
- **Sentry**: Error tracking and performance monitoring
- **New Relic**: Application performance monitoring
- **DataDog**: Infrastructure monitoring
- **Grafana**: Custom dashboards and alerts

### Logging Services
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Fluentd**: Log aggregation and forwarding
- **Papertrail**: Cloud log management

---

## 🎯 Deployment Checklist

### Pre-Deployment ✅
- [ ] Environment variables configured
- [ ] Database created and accessible
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Africa's Talking API tested
- [ ] Email service configured
- [ ] Backup strategy planned

### Post-Deployment ✅
- [ ] Application accessible via domain
- [ ] HTTPS working correctly
- [ ] Database connected
- [ ] Static files loading
- [ ] SMS functionality tested
- [ ] Email notifications working
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup system active

### Security ✅
- [ ] DEBUG = False
- [ ] Secret keys secure
- [ ] Database credentials secure
- [ ] SSL/TLS enabled
- [ ] Security headers configured
- [ ] CSRF protection enabled
- [ ] File permissions correct

---

**🚀 Ready for production deployment!**
