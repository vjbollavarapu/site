# Production Deployment Readiness Guide

## ✅ What's Already Done

- ✅ Docker setup (Dockerfile, docker-compose.prod.yml)
- ✅ Nginx configuration
- ✅ Deployment scripts (deploy.sh, migrate.sh, backup.sh)
- ✅ Health check endpoint (`/health/`)
- ✅ Email service configured
- ✅ Database migrations ready
- ✅ Security middleware configured
- ✅ Rate limiting configured
- ✅ CORS configured
- ✅ API documentation (Swagger/ReDoc)
- ✅ Postman collection

## ⚠️ Critical Production Settings Required

### 1. Environment Variables (.env.production)

Create `.env.production` file with these **REQUIRED** settings:

```bash
# Security (CRITICAL)
SECRET_KEY=<generate-secure-random-key-50-chars-min>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# HTTPS Security (REQUIRED for production)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/dbname
# OR individual settings:
DB_NAME=sitebackend_prod
DB_USER=sitebackend_user
DB_PASSWORD=<secure-password>
DB_HOST=your-db-host
DB_PORT=5432

# Redis
REDIS_URL=redis://redis-host:6379/0
CELERY_BROKER_URL=redis://redis-host:6379/0
CELERY_RESULT_BACKEND=redis://redis-host:6379/0

# Email (Already configured)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=oasys360.management@gmail.com
EMAIL_HOST_PASSWORD=<your-app-password>
DEFAULT_FROM_EMAIL=admin@oasys360.com
FRONTEND_URL=https://yourdomain.com

# Static & Media Files
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/mediafiles

# Optional: AWS S3 for static/media (recommended for production)
# USE_S3=True
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=us-east-1
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
```

### 2. Generate Secure SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Static Files Configuration

The project is configured to use Nginx for static files in production. Ensure:
- Static files are collected: `python manage.py collectstatic --noinput`
- Nginx is configured to serve static files (already done in `nginx/nginx.conf`)
- Or configure S3/CloudFront for static files (recommended for high traffic)

### 4. SSL/HTTPS Configuration

**Required for production:**
- SSL certificates installed
- Nginx configured with SSL (see `nginx/nginx.conf`)
- Update Nginx config to redirect HTTP to HTTPS
- Set `SECURE_SSL_REDIRECT=True` in `.env.production`

### 5. Database

- Production PostgreSQL database created
- Database user with proper permissions
- Connection tested
- Backup strategy in place

### 6. Celery Workers

For production, ensure Celery workers are running:
- Celery worker: `celery -A sitebackend worker -l info`
- Celery beat: `celery -A sitebackend beat -l info`
- Or use systemd/supervisor to manage as services

### 7. Monitoring & Logging

**Recommended:**
- Set up error tracking (Sentry, Rollbar, etc.)
- Configure logging to files
- Set up monitoring (New Relic, Datadog, etc.)
- Set up alerts for errors and downtime

## 🚀 Deployment Steps

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Create .env.production file
cp .env.example .env.production
# Edit .env.production with production values

# 2. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 4. Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 5. Create superuser (if needed)
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### Option 2: Manual Deployment

```bash
# 1. Set up virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set environment variables
export $(cat .env.production | xargs)

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Run with Gunicorn
gunicorn sitebackend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## ✅ Pre-Deployment Checklist

- [ ] `.env.production` file created with all required variables
- [ ] `SECRET_KEY` generated and set (50+ characters)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes production domain(s)
- [ ] `CORS_ALLOWED_ORIGINS` configured
- [ ] `CSRF_TRUSTED_ORIGINS` configured
- [ ] SSL certificates obtained and configured
- [ ] Database created and migrations ready
- [ ] Redis configured and accessible
- [ ] Email service tested
- [ ] Static files collection tested
- [ ] Health check endpoint tested (`/health/`)
- [ ] Celery workers configured
- [ ] Nginx configured with SSL
- [ ] Backup strategy in place
- [ ] Monitoring/logging configured

## 🔒 Security Checklist

- [ ] `SECRET_KEY` is secure (not default)
- [ ] `DEBUG=False`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SECURE_HSTS_SECONDS` set (31536000 = 1 year)
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] reCAPTCHA configured (if using)
- [ ] Database credentials secure
- [ ] No sensitive data in logs

## 📝 Post-Deployment Verification

1. **Health Check**: `curl https://yourdomain.com/health/`
2. **Admin Access**: `https://yourdomain.com/admin/`
3. **API Docs**: `https://yourdomain.com/api/docs/`
4. **Test Endpoints**:
   - Contact form submission
   - Waitlist join
   - Email verification
   - API endpoints

## 🆘 Rollback Plan

If deployment fails:
1. Stop new deployment
2. Restore previous version
3. Restore database backup (if needed)
4. Restart services
5. Investigate and fix issues

## 📚 Additional Resources

- Deployment Checklist: `DEPLOYMENT_CHECKLIST.md`
- Docker Setup: `docker-compose.prod.yml`
- Nginx Config: `nginx/nginx.conf`
- Deployment Script: `scripts/deploy.sh`

