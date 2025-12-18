# Production Nginx Configuration Guide

## Your Current Setup

You're running Django on port 8003 with Nginx as reverse proxy.
Static files should be at: `/var/www/python/site/staticfiles/`

## Updated Nginx Configuration

I've created `nginx/nginx.production.conf` with the correct configuration.

### Key Changes:
1. ✅ Added `/admin/static/` location for Django admin files
2. ✅ Added proper caching headers for static files
3. ✅ Improved proxy headers

## Steps to Fix on Production Server

### 1. Backup Current Config
```bash
sudo cp /etc/nginx/sites-available/site.bollavarapu.com /etc/nginx/sites-available/site.bollavarapu.com.backup
```

### 2. Update Nginx Config
```bash
# Edit your Nginx config
sudo nano /etc/nginx/sites-available/site.bollavarapu.com

# Or copy from the new config file
# (Update paths as needed)
```

### 3. Make Sure Static Files Are Collected
```bash
cd /var/www/python/site
source venv/bin/activate  # or your virtualenv path
python manage.py collectstatic --noinput
```

### 4. Verify Static Files Location
```bash
# Check if Django admin static files exist
ls -la /var/www/python/site/staticfiles/admin/css/
# Should see base.css and other admin CSS files
```

### 5. Test Nginx Configuration
```bash
sudo nginx -t
```

### 6. Reload Nginx
```bash
sudo systemctl reload nginx
```

### 7. Verify Static Files Are Served
```bash
# Test static file access
curl -I https://site.bollavarapu.com/static/admin/css/base.css
# Should return 200 OK, not 404

# Or check in browser:
# https://site.bollavarapu.com/static/admin/css/base.css
```

## Troubleshooting

### If static files still don't load:

1. **Check file permissions:**
   ```bash
   sudo chown -R www-data:www-data /var/www/python/site/staticfiles/
   sudo chmod -R 755 /var/www/python/site/staticfiles/
   ```

2. **Check Nginx error logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Verify STATIC_ROOT in Django settings:**
   ```python
   # In settings.py or .env
   STATIC_ROOT = '/var/www/python/site/staticfiles'
   ```

4. **Check if collectstatic ran successfully:**
   ```bash
   python manage.py collectstatic --noinput --verbosity 2
   ```

## Updated Config (Copy to your server)

See `nginx/nginx.production.conf` for the complete updated configuration.

