# Static Files Fix for Production

## Problem
Django admin CSS/JS not loading - admin page looks broken.

## Root Cause
Static files are not being served properly in production. Nginx needs to serve static files, not Django.

## Solution

### Option 1: Fix Nginx Configuration (Recommended)

The nginx.conf has been updated to serve static files. Make sure:

1. Static files are collected:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. Nginx has access to static files volume:
   - In docker-compose.prod.yml, nginx mounts staticfiles_prod volume
   - Static files should be at /app/staticfiles/ in the container

3. Restart Nginx:
   ```bash
   docker-compose restart nginx
   # or
   sudo systemctl restart nginx
   ```

### Option 2: Use WhiteNoise (Alternative - if not using Nginx)

If you're not using Nginx, install WhiteNoise:

1. Add to requirements.txt:
   ```
   whitenoise==6.6.0
   ```

2. Add to settings.py MIDDLEWARE:
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
       # ... rest of middleware
   ]
   ```

3. Add to settings.py:
   ```python
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   ```

### Option 3: Manual Fix on Production Server

If you're not using Docker:

1. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. Configure your web server (Nginx/Apache) to serve /static/ and /media/

3. Or use WhiteNoise (see Option 2)

## Verification

After fixing, check:
1. Visit: http://yourdomain.com/static/admin/css/base.css
   - Should return CSS content (not 404)

2. Check browser console for 404 errors on static files

3. Admin page should look normal with proper styling

