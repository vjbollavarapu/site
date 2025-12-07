# Quick Production Setup Guide

## 🚀 Before You Deploy

### 1. Create .env.production File

```bash
cp .env.example .env.production
```

### 2. Update .env.production with Production Values

**CRITICAL Settings:**
```bash
# Generate a new SECRET_KEY (50+ characters)
SECRET_KEY=<run: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">

DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# HTTPS Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_PROXY_SSL_HEADER=True
```

### 3. Deploy with Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Deployment

```bash
curl https://yourdomain.com/health/
```

## ✅ You're Ready!

See PRODUCTION_READINESS.md for complete checklist.

