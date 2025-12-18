# Site Backend API

Comprehensive Django REST Framework backend for landing page and marketing website. Includes contact submissions, waitlist management, lead capture, newsletter subscriptions, analytics tracking, and GDPR compliance.

## Table of Contents

- [Features](#features)
- [Project Overview](#project-overview)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Deployment Guide](#deployment-guide)
- [Testing](#testing)
- [Contributing](#contributing)

## Features

- **Contact Management**: Contact form submissions with spam detection
- **Waitlist Management**: Waitlist entry management with priority scoring
- **Lead Capture**: Lead management with scoring and CRM integration
- **Newsletter**: Newsletter subscription management with verification
- **Analytics**: Page view tracking, event tracking, and conversion tracking
- **GDPR Compliance**: Consent management, data export, and data deletion
- **CRM Integration**: HubSpot, Salesforce, and Pipedrive support
- **Email Service**: AWS SES and SendGrid integration
- **Security**: Rate limiting, honeypot protection, reCAPTCHA
- **Admin Dashboard**: Custom Django admin with statistics and charts

## Project Overview

This is a Django REST Framework backend designed for marketing websites and landing pages. It provides comprehensive APIs for managing contacts, leads, waitlist entries, newsletter subscriptions, and analytics data.

### Technology Stack

- **Framework**: Django 4.2+
- **API**: Django REST Framework 3.14+
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Documentation**: drf-spectacular (OpenAPI 3.0)

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis (for Celery)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sitebackend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Start Celery worker** (in separate terminal)
   ```bash
   celery -A sitebackend worker -l info
   ```

9. **Start Celery beat** (for scheduled tasks, in separate terminal)
   ```bash
   celery -A sitebackend beat -l info
   ```

### Access Points

- **API Documentation (Swagger)**: http://localhost:8000/api/docs/
- **API Documentation (ReDoc)**: http://localhost:8000/api/redoc/
- **Django Admin**: http://localhost:8000/admin/
- **API Schema**: http://localhost:8000/api/schema/

## Environment Variables

Create a `.env.local` file in the project root with the following variables:

### Required

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

### Optional

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # Development
# EMAIL_BACKEND=django_ses.SESBackend  # Production
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# SendGrid Alternative
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@example.com

# CRM Integration - HubSpot
HUBSPOT_API_KEY=your-hubspot-api-key
HUBSPOT_ACCESS_TOKEN=your-hubspot-access-token
HUBSPOT_PORTAL_ID=your-portal-id

# CRM Integration - Salesforce
SALESFORCE_USERNAME=your-username
SALESFORCE_PASSWORD=your-password
SALESFORCE_SECURITY_TOKEN=your-security-token
SALESFORCE_SANDBOX=False

# CRM Integration - Pipedrive
PIPEDRIVE_API_TOKEN=your-pipedrive-api-token

# Security
RECAPTCHA_PUBLIC_KEY=your-recaptcha-public-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-private-key

# Analytics
ANALYTICS_REQUIRE_CONSENT=True
ANALYTICS_EXTERNAL_ENABLED=False
GA4_MEASUREMENT_ID=your-ga4-measurement-id
GA4_API_SECRET=your-ga4-api-secret
MIXPANEL_TOKEN=your-mixpanel-token

# GDPR
GDPR_DATA_RETENTION_DEFAULT_DAYS=365
GDPR_ANONYMIZE_ON_DELETE_DEFAULT=True
```

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Authentication

Most endpoints require authentication. Use one of the following methods:

1. **Session Authentication**: Login via Django admin, then use session cookies
2. **Basic Authentication**: Include username and password in headers
   ```bash
   curl -u username:password http://localhost:8000/api/contacts/
   ```

### Rate Limiting

Public endpoints have rate limits:
- Contact submissions: 5 per IP per hour
- Lead capture: 10 per IP per hour
- Analytics tracking: 10 per IP per hour
- GDPR endpoints: 10 per IP per hour

## API Endpoints

### Contacts

- `POST /api/contacts/submit/` - Submit contact form (public)
- `GET /api/contacts/` - List contacts (admin)
- `GET /api/contacts/{id}/` - Get contact details (admin)
- `PATCH /api/contacts/{id}/` - Update contact (admin)
- `DELETE /api/contacts/{id}/` - Delete contact (admin)

### Waitlist

- `POST /api/waitlist/join/` - Join waitlist (public)
- `POST /api/waitlist/verify/` - Verify email (public)
- `GET /api/waitlist/status/{email}/` - Check waitlist status (public)
- `GET /api/waitlist/` - List waitlist entries (admin)

### Leads

- `POST /api/leads/capture/` - Capture lead (public)
- `POST /api/leads/{id}/track-event/` - Track lead event (public)
- `GET /api/leads/` - List leads (admin)
- `GET /api/leads/{id}/` - Get lead details (admin)
- `PATCH /api/leads/{id}/` - Update lead (admin)
- `POST /api/leads/{id}/qualify/` - Qualify lead (admin)
- `POST /api/leads/{id}/convert/` - Convert lead (admin)

### Newsletter

- `POST /api/newsletter/subscribe/` - Subscribe to newsletter (public)
- `POST /api/newsletter/verify/` - Verify email (public)
- `POST /api/newsletter/unsubscribe/` - Unsubscribe (public)
- `GET /api/newsletter/` - List subscriptions (admin)

### Analytics

- `POST /api/analytics/pageview/` - Track page view (public)
- `POST /api/analytics/event/` - Track event (public)
- `POST /api/analytics/conversion/` - Track conversion (public)
- `GET /api/analytics/dashboard/` - Get analytics dashboard (admin)

### GDPR

- `POST /api/gdpr/consent/` - Manage consent (public)
- `GET /api/gdpr/export/{email}/` - Export user data (public)
- `GET /api/gdpr/access/{email}/` - Access user data (public)
- `DELETE /api/gdpr/delete/{email}/` - Delete user data (public)

For detailed endpoint documentation, see the [Swagger UI](http://localhost:8000/api/docs/) or [ReDoc](http://localhost:8000/api/redoc/).

## Deployment Guide

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=False`
   - Set `SECRET_KEY` to a secure random value
   - Configure `ALLOWED_HOSTS`
   - Set up production database
   - Configure email backend
   - Set up Redis for Celery

2. **Database**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

3. **Static Files**
   - Configure static file serving (WhiteNoise, S3, etc.)
   - Run `python manage.py collectstatic`

4. **Celery**
   - Set up Celery worker as a service
   - Set up Celery beat for scheduled tasks
   - Configure Redis connection

5. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates

6. **Security**
   - Enable HTTPS
   - Configure CORS properly
   - Set up rate limiting
   - Enable reCAPTCHA
   - Review security settings

### Example Gunicorn Configuration

```bash
gunicorn sitebackend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/mediafiles/;
    }
}
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "sitebackend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Testing

See [README_TESTING.md](README_TESTING.md) for detailed testing information.

### Quick Test Commands

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure tests pass
6. Submit a pull request

## License

MIT License

## Support

For support, email support@example.com or open an issue in the repository.
