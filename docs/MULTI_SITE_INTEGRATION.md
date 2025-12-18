# Multi-Site Integration Guide

This guide explains how to integrate multiple websites with the backend API, including site detection, filtering, and best practices.

## Overview

The backend supports multiple websites/domains and automatically tracks which site each request comes from. This allows you to:

- Track data per site
- Filter analytics by site
- Manage multiple brands/products from one backend
- Analyze performance across sites

## Supported Sites

Default sites configured:

- **Oasys360**: `oasys360` - https://oasys360.com
- **Heals360**: `heals360` - https://heals360.com
- **Reliqo**: `reliqo` - https://reliqo.app
- **VCSMY**: `vcsmy` - https://vcsmy.com

## Site Detection

### Automatic Detection

The backend automatically detects the site from request headers:

1. **Origin Header** (Primary) - Used for CORS requests
2. **Referer Header** - Used as fallback
3. **Host Header** - Used as last resort
4. **X-Site-Identifier Header** - Explicit site ID (optional)

### How It Works

```typescript
// When you make a request from https://oasys360.com
fetch('https://api.backend.com/api/contacts/submit/', {
  method: 'POST',
  headers: {
    'Origin': 'https://oasys360.com', // Automatically set by browser
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
});

// Backend automatically detects: site = oasys360
```

### Explicit Site Identification

If automatic detection doesn't work, you can explicitly specify the site:

```typescript
// Option 1: Using X-Site-Identifier header
fetch('https://api.backend.com/api/contacts/submit/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Site-Identifier': 'site-uuid-here', // Get from admin
  },
  body: JSON.stringify(data),
});

// Option 2: Using site query parameter (for GET requests)
fetch('https://api.backend.com/api/contacts/?site=oasys360');
```

## Integration Patterns

### Pattern 1: Automatic Detection (Recommended)

**Use when:** Making requests from your websites directly

```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Origin header is automatically set by browser
  // No need to manually set it
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  return await response.json();
}
```

### Pattern 2: Explicit Site Parameter

**Use when:** You need to filter or specify site explicitly

```typescript
// For filtering queries
const site = 'oasys360'; // or get from context/config
const data = await apiRequest(`/api/contacts/?site=${site}`);

// For creating records with explicit site
const response = await apiRequest('/api/contacts/submit/', {
  method: 'POST',
  headers: {
    'X-Site-Identifier': siteId, // Optional, usually auto-detected
  },
  body: JSON.stringify(formData),
});
```

### Pattern 3: Site Context Provider

**Use when:** You want to manage site context across your app

```typescript
// contexts/site-context.tsx
'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface SiteContextType {
  site: string | null;
  setSite: (site: string | null) => void;
}

const SiteContext = createContext<SiteContextType | undefined>(undefined);

export function SiteProvider({ children }: { children: ReactNode }) {
  const [site, setSite] = useState<string | null>(null);

  // Auto-detect site from current domain
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      const siteMap: Record<string, string> = {
        'oasys360.com': 'oasys360',
        'heals360.com': 'heals360',
        'reliqo.app': 'reliqo',
        'vcsmy.com': 'vcsmy',
      };
      
      const detectedSite = siteMap[hostname] || 
                          Object.keys(siteMap).find(key => hostname.includes(key));
      
      if (detectedSite) {
        setSite(siteMap[detectedSite] || detectedSite);
      }
    }
  }, []);

  return (
    <SiteContext.Provider value={{ site, setSite }}>
      {children}
    </SiteContext.Provider>
  );
}

export function useSite() {
  const context = useContext(SiteContext);
  if (!context) {
    throw new Error('useSite must be used within SiteProvider');
  }
  return context;
}
```

## Filtering by Site

### Dashboard Stats

```typescript
// Get stats for specific site
const stats = await apiRequest('/api/dashboard/stats/?site=oasys360');

// Get stats for all sites (default)
const allStats = await apiRequest('/api/dashboard/stats/');
```

### Analytics

```typescript
// Get analytics for specific site
const analytics = await apiRequest(
  '/api/analytics/dashboard/?site=heals360&date_from=2024-01-01&date_to=2024-01-31'
);
```

### List Endpoints

```typescript
// Get contacts for specific site
const contacts = await apiRequest('/api/contacts/?site=reliqo');

// Get waitlist entries for specific site
const entries = await apiRequest('/api/waitlist/entries/?site=vcsmy');

// Get leads for specific site
const leads = await apiRequest('/api/leads/?site=oasys360');
```

## Site-Specific Configuration

### Environment-Based Site Detection

```typescript
// lib/site-config.ts
export const SITE_CONFIG = {
  oasys360: {
    name: 'Oasys360',
    domain: 'oasys360.com',
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    theme: 'blue',
  },
  heals360: {
    name: 'Heals360',
    domain: 'heals360.com',
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    theme: 'green',
  },
  reliqo: {
    name: 'Reliqo',
    domain: 'reliqo.app',
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    theme: 'purple',
  },
  vcsmy: {
    name: 'VCSMY',
    domain: 'vcsmy.com',
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    theme: 'orange',
  },
};

export function getSiteFromHostname(hostname: string): string | null {
  for (const [key, config] of Object.entries(SITE_CONFIG)) {
    if (hostname.includes(config.domain)) {
      return key;
    }
  }
  return null;
}

export function getCurrentSite(): string | null {
  if (typeof window === 'undefined') return null;
  return getSiteFromHostname(window.location.hostname);
}
```

### Using Site Config

```typescript
// components/contact-form.tsx
import { getCurrentSite, SITE_CONFIG } from '@/lib/site-config';

export function ContactForm() {
  const currentSite = getCurrentSite();
  const siteConfig = currentSite ? SITE_CONFIG[currentSite] : null;

  return (
    <div className={`theme-${siteConfig?.theme || 'default'}`}>
      <form>
        {/* Form content */}
      </form>
    </div>
  );
}
```

## Best Practices

### 1. Always Let Backend Detect Site

Don't manually set site unless necessary. The backend's automatic detection is reliable.

```typescript
// ✅ Good - Let backend detect
await apiRequest('/api/contacts/submit/', {
  method: 'POST',
  body: JSON.stringify(data),
});

// ❌ Avoid - Manual site setting (unless needed)
await apiRequest('/api/contacts/submit/', {
  method: 'POST',
  headers: {
    'X-Site-Identifier': siteId, // Usually not needed
  },
  body: JSON.stringify(data),
});
```

### 2. Use Site Filtering for Admin Views

```typescript
// ✅ Good - Filter by site in admin views
const contacts = await apiRequest(`/api/contacts/?site=${currentSite}`);

// ❌ Avoid - Getting all contacts when you only need one site
const allContacts = await apiRequest('/api/contacts/');
```

### 3. Store Site in Context

```typescript
// ✅ Good - Use context for site
const { site } = useSite();
const stats = await apiRequest(`/api/dashboard/stats/?site=${site}`);

// ❌ Avoid - Hardcoding site
const stats = await apiRequest('/api/dashboard/stats/?site=oasys360');
```

### 4. Handle Site Detection Errors

```typescript
try {
  const data = await apiRequest('/api/contacts/submit/', {
    method: 'POST',
    body: JSON.stringify(formData),
  });
} catch (error) {
  // If site detection fails, backend uses default site
  // Still log for debugging
  console.warn('Site detection may have failed:', error);
}
```

## Testing Multi-Site

### Test from Different Domains

```typescript
// test-multi-site.ts
async function testMultiSite() {
  const sites = ['oasys360', 'heals360', 'reliqo', 'vcsmy'];

  for (const site of sites) {
    console.log(`Testing ${site}...`);
    
    // Test contact form
    const contactResponse = await apiRequest('/api/contacts/submit/', {
      method: 'POST',
      headers: {
        'Origin': `https://${SITE_CONFIG[site].domain}`,
      },
      body: JSON.stringify({
        name: 'Test User',
        email: `test@${SITE_CONFIG[site].domain}`,
        subject: 'Test',
        message: 'Test message',
      }),
    });
    
    console.log(`✓ ${site} contact form works`);
  }
}
```

### Verify Site Tracking

```typescript
// Verify that data is tagged with correct site
const contacts = await apiRequest('/api/contacts/');
contacts.results.forEach(contact => {
  console.log(`Contact ${contact.email} from site: ${contact.site?.name}`);
});
```

## Troubleshooting

### Site Not Detected

**Problem:** Requests show `site: null` in backend

**Solutions:**
1. Check CORS configuration includes your domain
2. Verify `Origin` header is being sent
3. Use explicit `X-Site-Identifier` header as fallback
4. Check backend logs for site detection errors

### Wrong Site Detected

**Problem:** Requests are tagged with wrong site

**Solutions:**
1. Check domain mapping in Site model
2. Verify `additional_domains` includes all variants (www, subdomains)
3. Use explicit site identification if needed

### Site Filtering Not Working

**Problem:** Filtering by site returns no results

**Solutions:**
1. Verify site name/ID is correct
2. Check site is active in database
3. Verify data actually has site assigned
4. Check query parameter spelling

## Migration Guide

### Existing Data

If you have existing data without site assignment:

1. Run migrations to add site field
2. Existing records will have `site: null`
3. Optionally, assign default site to existing data:

```python
# management/command/assign_default_site.py
from apps.core.models import Site
from apps.contacts.models import ContactSubmission

default_site = Site.objects.filter(is_default=True).first()
if default_site:
    ContactSubmission.objects.filter(site__isnull=True).update(site=default_site)
```

### Adding New Sites

1. Add site in Django admin or via management command
2. Update CORS settings
3. Update frontend site config if needed
4. Test site detection

## Examples

See `INTEGRATION_GUIDE.md` for complete code examples with multi-site support.

