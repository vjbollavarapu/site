# Quick Start Guide

Get up and running with the backend API integration in minutes.

## Prerequisites

- Backend running at `http://localhost:8000` (or configured URL)
- Frontend application (Next.js, React, etc.)
- Basic understanding of REST APIs

## 1. Setup API Client

Create an API client utility:

```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      message: `HTTP error! status: ${response.status}` 
    }));
    throw new Error(error.message || error.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}
```

## 2. Contact Form Integration

```typescript
// components/contact-form.tsx
'use client';

import { useState } from 'react';
import { apiRequest } from '@/lib/api-client';

export function ContactForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiRequest('/api/contacts/submit/', {
        method: 'POST',
        body: JSON.stringify(formData),
      });

      if (response.success) {
        setSuccess(true);
        setFormData({ name: '', email: '', subject: '', message: '' });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="Name"
        required
      />
      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        placeholder="Email"
        required
      />
      <input
        type="text"
        value={formData.subject}
        onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
        placeholder="Subject"
        required
      />
      <textarea
        value={formData.message}
        onChange={(e) => setFormData({ ...formData, message: e.target.value })}
        placeholder="Message"
        required
        minLength={10}
      />
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Thank you for your submission!</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

## 3. Waitlist Integration

```typescript
// components/waitlist-form.tsx
'use client';

import { useState } from 'react';
import { apiRequest } from '@/lib/api-client';

export function WaitlistForm() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiRequest('/api/waitlist/join/', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });

      if (response.success) {
        setSuccess(true);
        setEmail('');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
      />
      {error && <div className="error">{error}</div>}
      {success && (
        <div className="success">
          Please check your email to verify your subscription!
        </div>
      )}
      <button type="submit" disabled={loading}>
        {loading ? 'Joining...' : 'Join Waitlist'}
      </button>
    </form>
  );
}
```

## 4. Analytics Tracking

```typescript
// lib/analytics.ts
import { apiRequest } from './api-client';

let sessionId: string | null = null;

function getSessionId(): string {
  if (!sessionId) {
    sessionId = localStorage.getItem('analytics_session_id') || 
                `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('analytics_session_id', sessionId);
  }
  return sessionId;
}

export async function trackPageView(pageUrl: string, pageTitle?: string) {
  try {
    await apiRequest('/api/analytics/pageview/', {
      method: 'POST',
      body: JSON.stringify({
        page_url: pageUrl,
        page_title: pageTitle || document.title,
        session_id: getSessionId(),
      }),
    });
  } catch (error) {
    // Silently fail
    console.error('Analytics tracking failed:', error);
  }
}

export async function trackEvent(
  eventName: string,
  category: string = 'user_interaction',
  properties?: Record<string, any>
) {
  try {
    await apiRequest('/api/analytics/event/', {
      method: 'POST',
      body: JSON.stringify({
        event_name: eventName,
        event_category: category,
        event_properties: properties || {},
        session_id: getSessionId(),
        page_url: window.location.href,
      }),
    });
  } catch (error) {
    console.error('Event tracking failed:', error);
  }
}
```

## 5. Use Analytics in Your App

```typescript
// app/layout.tsx or _app.tsx
'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { trackPageView } from '@/lib/analytics';

export function AnalyticsProvider({ children }) {
  const pathname = usePathname();

  useEffect(() => {
    trackPageView(window.location.href, document.title);
  }, [pathname]);

  return <>{children}</>;
}

// components/button.tsx
import { trackEvent } from '@/lib/analytics';

export function CTAButton() {
  const handleClick = () => {
    trackEvent('cta_click', 'conversion', {
      button_id: 'hero-cta',
      page: window.location.pathname,
    });
    // Handle click
  };

  return <button onClick={handleClick}>Get Started</button>;
}
```

## 6. Environment Configuration

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Test Contact Form

```typescript
// Test contact form submission
const testContact = async () => {
  try {
    const response = await apiRequest('/api/contacts/submit/', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Test User',
        email: 'test@example.com',
        subject: 'Test',
        message: 'This is a test message',
      }),
    });
    console.log('✓ Contact form works:', response);
  } catch (error) {
    console.error('✗ Contact form failed:', error);
  }
};
```

### Test Waitlist

```typescript
// Test waitlist join
const testWaitlist = async () => {
  try {
    const response = await apiRequest('/api/waitlist/join/', {
      method: 'POST',
      body: JSON.stringify({
        email: 'test@example.com',
      }),
    });
    console.log('✓ Waitlist join works:', response);
  } catch (error) {
    console.error('✗ Waitlist join failed:', error);
  }
};
```

## Next Steps

1. **Read Full Documentation**: See `INTEGRATION_GUIDE.md` for comprehensive guide
2. **API Reference**: See `API_REFERENCE.md` for all endpoints
3. **Multi-Site**: See `MULTI_SITE_INTEGRATION.md` for multi-site support
4. **Error Handling**: Implement proper error handling (see examples in `INTEGRATION_GUIDE.md`)
5. **Authentication**: Set up admin authentication for protected endpoints

## Common Issues

### CORS Errors

**Problem:** `Access-Control-Allow-Origin` error

**Solution:** Ensure your domain is in `CORS_ALLOWED_ORIGINS` in backend settings

### 503 Service Unavailable

**Problem:** Backend not running

**Solution:** Start backend server: `python manage.py runserver`

### 401 Unauthorized

**Problem:** Admin endpoint requires authentication

**Solution:** Add Basic Auth header (see Authentication section in `INTEGRATION_GUIDE.md`)

### Rate Limit Exceeded

**Problem:** Too many requests

**Solution:** Wait before retrying, or implement exponential backoff

## Support

- Full documentation: See other files in `/docs` folder
- API docs: Visit `/api/docs/` (Swagger UI) or `/api/redoc/` (ReDoc)
- Backend logs: Check Django logs for detailed errors

