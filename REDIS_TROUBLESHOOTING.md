# Redis Connection Troubleshooting

## Problem
Error: `Error 111 connecting to localhost:6379. Connection refused`

This means Redis is not running or not accessible on your production server.

## Solutions

### Option 1: Install and Start Redis (Recommended)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**CentOS/RHEL:**
```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### Option 2: Use Docker Redis

If using Docker, ensure Redis container is running:
```bash
docker-compose up -d redis
```

### Option 3: Disable Redis (Fallback)

If you don't want to use Redis, the code now handles Redis failures gracefully.
However, you should update your settings to use LocMemCache:

In `.env.production`:
```bash
# Don't set REDIS_URL, or set it to empty
REDIS_URL=
```

The application will automatically fall back to LocMemCache (in-memory cache).

### Option 4: Configure Redis Connection

If Redis is on a different host/port, update `.env.production`:
```bash
REDIS_URL=redis://your-redis-host:6379/0
```

## Verification

After fixing Redis, restart your Django application:
```bash
# If using systemd
sudo systemctl restart gunicorn

# If using Docker
docker-compose restart web
```

## Note

The analytics middleware now handles Redis connection failures gracefully.
The application will continue to work even if Redis is unavailable, but:
- Session tracking will be limited (cookie-based only)
- Cache-dependent features may not work optimally
- Analytics data will still be saved to the database

For production, Redis is recommended for:
- Better performance
- Session management
- Rate limiting
- Celery task queue

