# Troubleshooting Static Files - Step by Step

## Quick Fix: Use WhiteNoise (Recommended)

If Nginx static file serving isn't working, use WhiteNoise - it's simpler and works reliably.

### Step 1: Install WhiteNoise
```bash
pip install whitenoise
# Add to requirements.txt: whitenoise==6.6.0
```

### Step 2: Update settings.py
Add WhiteNoise to MIDDLEWARE (right after SecurityMiddleware):

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ADD THIS
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of middleware
]
```

### Step 3: Add to settings.py
```python
# Static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Step 4: Collect static files
```bash
python manage.py collectstatic --noinput
```

### Step 5: Restart Django
```bash
# If using systemd
sudo systemctl restart gunicorn

# If using supervisor
sudo supervisorctl restart sitebackend

# If running manually
# Stop and restart your Django process
```

## Alternative: Fix Nginx Configuration

### Step 1: Verify Static Files Exist
```bash
ls -la /var/www/python/site/staticfiles/admin/css/
# Should see base.css, dashboard.css, etc.
```

### Step 2: Check File Permissions
```bash
sudo chown -R www-data:www-data /var/www/python/site/staticfiles/
sudo chmod -R 755 /var/www/python/site/staticfiles/
```

### Step 3: Check Nginx Error Logs
```bash
sudo tail -f /var/log/nginx/error.log
# Try accessing admin page and see if errors appear
```

### Step 4: Test Static File Access
```bash
# Test if Nginx can access the files
sudo -u www-data ls /var/www/python/site/staticfiles/admin/css/
```

### Step 5: Verify Nginx Config Syntax
```bash
sudo nginx -t
# Should say "syntax is ok"
```

### Step 6: Check if Nginx Config Was Reloaded
```bash
sudo systemctl status nginx
sudo systemctl reload nginx
# Or restart:
sudo systemctl restart nginx
```

## Debug: Check What's Happening

### 1. Check Browser Console
- Open browser DevTools (F12)
- Go to Network tab
- Reload admin page
- Look for 404 errors on CSS/JS files
- Check the URL it's trying to load

### 2. Test Static File URL Directly
```bash
# In browser, try:
https://site.bollavarapu.com/static/admin/css/base.css

# Or with curl:
curl -I https://site.bollavarapu.com/static/admin/css/base.css
# Should return 200 OK, not 404
```

### 3. Check Django STATIC_URL Setting
```python
# In settings.py, verify:
STATIC_URL = 'static/'  # or '/static/'
STATIC_ROOT = '/var/www/python/site/staticfiles'
```

### 4. Check if collectstatic ran
```bash
cd /var/www/python/site
python manage.py collectstatic --noinput --verbosity 2
# Should show files being copied
```

## Common Issues

### Issue 1: STATIC_URL mismatch
- Django expects `/static/` but Nginx serves from different path
- Solution: Make sure STATIC_URL in settings matches Nginx location

### Issue 2: Files not collected
- collectstatic didn't run or failed silently
- Solution: Run collectstatic with --verbosity 2 to see errors

### Issue 3: Wrong permissions
- Nginx user (www-data) can't read files
- Solution: Fix ownership and permissions (see Step 2 above)

### Issue 4: Nginx config not reloaded
- Changes made but Nginx not restarted
- Solution: Always run `sudo nginx -t` then `sudo systemctl reload nginx`

### Issue 5: Browser cache
- Browser showing old cached version
- Solution: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

## Recommended Solution: WhiteNoise

WhiteNoise is the easiest solution - it serves static files directly from Django,
no Nginx configuration needed. It's production-ready and used by many Django apps.

