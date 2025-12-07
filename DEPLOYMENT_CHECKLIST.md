# Deployment Checklist

## Pre-Deployment

### Code Quality
- [ ] All tests passing (`python manage.py test`)
- [ ] Code coverage above 80% (`coverage report`)
- [ ] No linting errors
- [ ] Code review completed
- [ ] Documentation updated

### Environment Configuration
- [ ] Environment variables configured in `.env.production`
- [ ] `SECRET_KEY` set to secure random value
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured with production domain(s)
- [ ] `CORS_ALLOWED_ORIGINS` configured
- [ ] `CSRF_TRUSTED_ORIGINS` configured

### Database
- [ ] Database migrations reviewed (`python manage.py makemigrations --dry-run`)
- [ ] Database migrations ready (`python manage.py showmigrations`)
- [ ] Database backup created (if updating existing)
- [ ] Database connection tested

### Static & Media Files
- [ ] Static files collected (`python manage.py collectstatic --noinput`)
- [ ] Media files storage configured (local or S3)
- [ ] Static files serving configured (WhiteNoise, Nginx, or S3)
- [ ] CDN configured (if using)

### Security
- [ ] `SECRET_KEY` is secure and unique
- [ ] `DEBUG=False` in production
- [ ] HTTPS enabled
- [ ] SSL certificates configured
- [ ] Security headers configured
- [ ] Rate limiting configured
- [ ] reCAPTCHA configured and tested
- [ ] Honeypot protection enabled
- [ ] CORS properly configured
- [ ] Session cookies secure (`SESSION_COOKIE_SECURE=True`)
- [ ] CSRF cookies secure (`CSRF_COOKIE_SECURE=True`)

### Email Service
- [ ] Email backend configured (SES, SendGrid, or SMTP)
- [ ] Email credentials tested
- [ ] Test email sent successfully
- [ ] Email templates reviewed
- [ ] `DEFAULT_FROM_EMAIL` configured

### CRM Integration
- [ ] CRM provider selected and configured
- [ ] CRM credentials tested
- [ ] CRM field mapping configured
- [ ] Test sync performed
- [ ] Error handling verified

### Monitoring & Logging
- [ ] Logging configuration set up
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Monitoring tools configured
- [ ] Health check endpoints tested
- [ ] Alerting configured

### Performance
- [ ] Database indexes reviewed
- [ ] Query optimization reviewed
- [ ] Caching configured (Redis)
- [ ] Celery workers configured
- [ ] Celery beat configured for scheduled tasks

## Deployment

### Staging Deployment
- [ ] Deploy to staging environment first
- [ ] Run database migrations (`python manage.py migrate`)
- [ ] Collect static files (`python manage.py collectstatic --noinput`)
- [ ] Restart application services
- [ ] Restart Celery workers
- [ ] Restart Celery beat
- [ ] Health check passes
- [ ] Smoke tests pass

### Production Deployment
- [ ] Database backup created
- [ ] Run database migrations (`python manage.py migrate`)
- [ ] Collect static files (`python manage.py collectstatic --noinput`)
- [ ] Restart application services (zero-downtime if possible)
- [ ] Restart Celery workers
- [ ] Restart Celery beat
- [ ] Health check passes
- [ ] Smoke tests pass

### Docker Deployment (if using)
- [ ] Docker images built
- [ ] Docker images pushed to registry
- [ ] `docker-compose.prod.yml` configured
- [ ] Environment variables set in `.env.production`
- [ ] Services started (`docker-compose -f docker-compose.prod.yml up -d`)
- [ ] Health checks passing
- [ ] Logs reviewed

## Post-Deployment

### Verification
- [ ] Application accessible at production URL
- [ ] Admin interface accessible
- [ ] API documentation accessible (`/api/docs/`)
- [ ] Health check endpoint responding
- [ ] Error logs reviewed (no critical errors)

### Functional Testing
- [ ] Contact form submission tested
- [ ] Waitlist signup tested
- [ ] Lead capture tested
- [ ] Newsletter subscription tested
- [ ] Email verification tested
- [ ] Analytics tracking verified
- [ ] GDPR endpoints tested

### Integration Testing
- [ ] Email sending verified
- [ ] CRM sync verified
- [ ] Webhook delivery verified (if enabled)
- [ ] External analytics verified (if enabled)

### Performance Monitoring
- [ ] Response times acceptable
- [ ] Database query performance acceptable
- [ ] No memory leaks detected
- [ ] Celery tasks processing correctly
- [ ] Cache hit rates acceptable

### Security Verification
- [ ] HTTPS working correctly
- [ ] Security headers present
- [ ] Rate limiting working
- [ ] CORS configured correctly
- [ ] No sensitive data in logs

### Rollback Plan
- [ ] Rollback procedure documented
- [ ] Database rollback script ready
- [ ] Previous version tagged
- [ ] Rollback tested in staging

## Ongoing Maintenance

### Daily
- [ ] Monitor error logs
- [ ] Check application health
- [ ] Review failed tasks

### Weekly
- [ ] Review analytics data
- [ ] Check CRM sync status
- [ ] Review security logs
- [ ] Performance metrics review

### Monthly
- [ ] Database maintenance
- [ ] Log rotation
- [ ] Security updates
- [ ] Dependency updates review
- [ ] Backup verification

## Emergency Procedures

### If Deployment Fails
1. Stop deployment immediately
2. Check error logs
3. Rollback to previous version
4. Investigate issue
5. Fix and redeploy

### If Database Migration Fails
1. Stop application
2. Restore database from backup
3. Investigate migration issue
4. Fix migration
5. Test in staging
6. Redeploy

### If Application Crashes
1. Check application logs
2. Check system resources
3. Restart services
4. Investigate root cause
5. Apply fix

