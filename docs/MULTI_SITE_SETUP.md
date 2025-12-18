# Multi-Site Support Setup Guide

This application now supports tracking and managing data from multiple websites/domains.

## Supported Sites

- **Oasys360**: https://oasys360.com
- **Heals360**: https://heals360.com
- **Reliqo**: https://reliqo.app
- **VCSMY**: https://vcsmy.com

## Features

1. **Site Detection**: Automatically detects which site a request comes from using:
   - `Origin` header
   - `Referer` header
   - `Host` header
   - Custom `X-Site-Identifier` header (for API calls)

2. **Data Tracking**: All data (contacts, waitlist, leads, newsletter, analytics) is tagged with the originating site

3. **Filtering & Analytics**: Dashboard and analytics can filter by site

4. **CORS Configuration**: All sites are automatically allowed in CORS settings

## Setup Instructions

### 1. Run Migrations

```bash
cd apps/backend
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Default Sites

```bash
python manage.py setup_sites
```

This will create the four default sites in the database.

### 3. Configure CORS (Optional)

The default sites are already configured in `settings.py`. If you need to add more sites, update:

```python
DEFAULT_SITES = [
    'https://oasys360.com',
    'https://heals360.com',
    'https://reliqo.app',
    'https://vcsmy.com',
    # Add more sites here
]
```

Or set `CORS_ALLOWED_ORIGINS` in your `.env` file:

```env
CORS_ALLOWED_ORIGINS=https://oasys360.com,https://heals360.com,https://reliqo.app,https://vcsmy.com
```

## Using Multi-Site Support

### Frontend Integration

When making API calls from your websites, the site is automatically detected from the `Origin` header. However, you can also explicitly specify the site:

```javascript
// Option 1: Automatic detection (from Origin header)
fetch('https://api.yourbackend.com/api/contacts/submit/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({...})
});

// Option 2: Explicit site identifier
fetch('https://api.yourbackend.com/api/contacts/submit/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Site-Identifier': 'site-uuid-here', // Optional: explicit site ID
  },
  body: JSON.stringify({...})
});
```

### Backend API Filtering

All API endpoints support filtering by site:

```python
# Get contacts for a specific site
GET /api/contacts/?site=oasys360

# Get waitlist entries for a specific site
GET /api/waitlist/entries/?site=heals360

# Get analytics for a specific site
GET /api/analytics/dashboard/?site=reliqo&date_from=2024-01-01
```

### Dashboard Filtering

The dashboard stats endpoint supports site filtering:

```python
GET /api/dashboard/stats/?site=oasys360
```

## Admin Interface

You can manage sites in the Django admin:

1. Go to `/admin/core/site/`
2. View, edit, or create sites
3. Set a default site (used when site cannot be detected)
4. Enable/disable sites

## Site Model Fields

- `name`: Internal identifier (e.g., "oasys360")
- `domain`: Primary domain (e.g., "oasys360.com")
- `display_name`: Display name (e.g., "Oasys360")
- `base_url`: Full URL (e.g., "https://oasys360.com")
- `is_active`: Whether the site is active
- `is_default`: Default site for requests without site identifier
- `additional_domains`: List of additional domains (e.g., ["www.oasys360.com"])

## Data Models with Site Tracking

All these models now have a `site` foreign key:

- `ContactSubmission`
- `WaitlistEntry`
- `Lead`
- `NewsletterSubscription`
- `PageView` (Analytics)
- `Event` (Analytics)
- `Conversion` (Analytics)

## Querying by Site

```python
from apps.core.models import Site
from apps.contacts.models import ContactSubmission

# Get site
site = Site.objects.get(name='oasys360')

# Get all contacts for this site
contacts = ContactSubmission.objects.filter(site=site)

# Get all contacts for a site by domain
site = Site.get_site_from_domain('oasys360.com')
contacts = ContactSubmission.objects.filter(site=site)
```

## Notes

- If a site cannot be detected, the default site is used (if set)
- Site detection is automatic and doesn't require any changes to existing frontend code
- All existing data will have `site=None` until migrations are run
- You can manually assign sites to existing data in the admin interface

