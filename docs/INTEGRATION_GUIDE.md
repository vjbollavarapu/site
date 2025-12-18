# Backend Integration Guide

This guide provides comprehensive documentation for integrating frontend applications with the Django backend API. This documentation is designed to be understood by AI assistants like Cursor.AI for automated integration.

## Table of Contents

1. [Overview](#overview)
2. [API Base Configuration](#api-base-configuration)
3. [Authentication](#authentication)
4. [Multi-Site Support](#multi-site-support)
5. [API Endpoints](#api-endpoints)
6. [Error Handling](#error-handling)
7. [Code Examples](#code-examples)
8. [Best Practices](#best-practices)

## Overview

The backend provides a RESTful API built with Django REST Framework. All endpoints are prefixed with `/api/` and return JSON responses.

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure via `NEXT_PUBLIC_API_URL` environment variable

### API Versioning

Currently using unversioned endpoints. All endpoints are under `/api/`.

## API Base Configuration

### Environment Variables

```env
# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Client Setup

```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authentication if available
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Basic ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
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

## Authentication

### Admin Authentication

Admin endpoints require Basic Authentication using Django admin credentials.

```typescript
// lib/auth.ts
export function createBasicAuthToken(username: string, password: string): string {
  return btoa(`${username}:${password}`);
}

export async function login(username: string, password: string) {
  const token = createBasicAuthToken(username, password);
  
  // Test authentication
  const response = await fetch(`${API_BASE_URL}/api/contacts/`, {
    headers: {
      'Authorization': `Basic ${token}`,
    },
  });

  if (response.ok) {
    setAuthToken(token);
    return { success: true };
  }
  
  return { success: false, error: 'Invalid credentials' };
}
```

### Public Endpoints

These endpoints don't require authentication:
- `/api/contacts/submit/` - Contact form submission
- `/api/waitlist/join/` - Join waitlist
- `/api/waitlist/verify/` - Verify waitlist email
- `/api/waitlist/status/:email/` - Check waitlist status
- `/api/leads/capture/` - Capture lead
- `/api/newsletter/subscribe/` - Subscribe to newsletter
- `/api/newsletter/verify/` - Verify newsletter subscription
- `/api/newsletter/unsubscribe/` - Unsubscribe from newsletter
- `/api/analytics/pageview/` - Track page view
- `/api/analytics/event/` - Track event

## Multi-Site Support

The backend automatically detects which site a request comes from using the `Origin` header. You can also explicitly specify the site.

### Automatic Detection

Site is automatically detected from the `Origin` header when making requests from your websites.

### Explicit Site Identification

```typescript
// Option 1: Using X-Site-Identifier header
fetch(`${API_BASE_URL}/api/contacts/submit/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Site-Identifier': 'site-uuid-here', // Optional
  },
  body: JSON.stringify(data),
});

// Option 2: Filtering by site in queries
fetch(`${API_BASE_URL}/api/contacts/?site=oasys360`);
```

### Supported Sites

- `oasys360` - https://oasys360.com
- `heals360` - https://heals360.com
- `reliqo` - https://reliqo.app
- `vcsmy` - https://vcsmy.com

## API Endpoints

### Contacts

#### Submit Contact Form (Public)

```typescript
POST /api/contacts/submit/

Request Body:
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry",
  "message": "Message content",
  "phone": "+1234567890", // Optional
  "company": "Company Name", // Optional
  "recaptcha_token": "token" // Optional, if reCAPTCHA enabled
}

Response (201):
{
  "success": true,
  "submission_id": "uuid",
  "message": "Thank you for your submission."
}
```

#### List Contacts (Admin)

```typescript
GET /api/contacts/
GET /api/contacts/?site=oasys360
GET /api/contacts/?status=new
GET /api/contacts/?search=john

Response (200):
{
  "results": [...],
  "count": 100,
  "next": "url",
  "previous": "url"
}
```

#### Get Contact (Admin)

```typescript
GET /api/contacts/:id/

Response (200):
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  ...
}
```

### Waitlist

#### Join Waitlist (Public)

```typescript
POST /api/waitlist/join/

Request Body:
{
  "email": "user@example.com",
  "name": "John Doe", // Optional
  "company": "Company", // Optional
  "ab_test_name": "landing_page_variant" // Optional
}

Response (201):
{
  "success": true,
  "entry_id": "uuid",
  "message": "Please check your email to verify your subscription."
}
```

#### Verify Waitlist Email (Public)

```typescript
POST /api/waitlist/verify/

Request Body:
{
  "token": "verification-token"
}

Response (200):
{
  "success": true,
  "message": "Your email has been verified!"
}
```

#### Check Waitlist Status (Public)

```typescript
GET /api/waitlist/status/:email/

Response (200):
{
  "email": "user@example.com",
  "status": "pending",
  "priority_score": 75,
  "is_verified": false
}
```

### Leads

#### Capture Lead (Public)

```typescript
POST /api/leads/capture/

Request Body:
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890", // Optional
  "company": "Company", // Optional
  "ab_test_name": "lead_form_variant" // Optional
}

Response (201):
{
  "success": true,
  "lead_id": "uuid",
  "message": "Lead captured successfully."
}
```

### Newsletter

#### Subscribe (Public)

```typescript
POST /api/newsletter/subscribe/

Request Body:
{
  "email": "user@example.com",
  "name": "John Doe", // Optional
  "preference": "weekly", // Optional: daily, weekly, monthly
  "interests": ["tech", "healthcare"] // Optional
}

Response (201):
{
  "success": true,
  "message": "Please check your email to verify your subscription."
}
```

#### Verify Subscription (Public)

```typescript
POST /api/newsletter/verify/

Request Body:
{
  "token": "verification-token"
}

Response (200):
{
  "success": true,
  "message": "Your subscription has been verified!"
}
```

### Analytics

#### Track Page View (Public)

```typescript
POST /api/analytics/pageview/

Request Body:
{
  "page_url": "https://example.com/page",
  "page_title": "Page Title", // Optional
  "referrer_url": "https://google.com", // Optional
  "duration": 45.5, // Optional, seconds
  "session_id": "session-id" // Optional, auto-generated
}

Response (201):
{
  "success": true,
  "session_id": "session-id",
  "pageview_id": "uuid"
}
```

#### Track Event (Public)

```typescript
POST /api/analytics/event/

Request Body:
{
  "event_name": "button_click",
  "event_category": "user_interaction",
  "event_value": 10.5, // Optional
  "event_properties": { // Optional
    "button_id": "cta-primary"
  },
  "page_url": "https://example.com/page", // Optional
  "session_id": "session-id" // Optional
}

Response (201):
{
  "success": true,
  "event_id": "uuid",
  "session_id": "session-id"
}
```

### Dashboard

#### Get Dashboard Stats (Admin)

```typescript
GET /api/dashboard/stats/
GET /api/dashboard/stats/?site=oasys360

Response (200):
{
  "contacts": {
    "total": 100,
    "new": 10,
    "pending": 5,
    "trend": 12.5
  },
  "waitlist": {
    "total": 50,
    "pending": 3,
    "avgScore": 7.8,
    "trend": 8.3
  },
  "leads": {
    "total": 75,
    "qualified": 20,
    "conversionRate": 15.8,
    "trend": -2.1
  },
  "newsletter": {
    "total": 200,
    "active": 180,
    "unsubscribes": 5,
    "growthRate": 18.7
  },
  "site": { // If filtered by site
    "id": "uuid",
    "name": "oasys360",
    "domain": "oasys360.com",
    "display_name": "Oasys360"
  }
}
```

### Analytics Dashboard

#### Get Analytics Dashboard (Admin)

```typescript
GET /api/analytics/dashboard/
GET /api/analytics/dashboard/?date_from=2024-01-01&date_to=2024-01-31
GET /api/analytics/dashboard/?site=oasys360

Response (200):
{
  "overview": {
    "total_pageviews": 1000,
    "unique_visitors": 500,
    "avg_session_duration": 120.5,
    "bounce_rate": 45.2
  },
  "top_pages": [
    {
      "page_url": "/",
      "page_title": "Home",
      "views": 500,
      "unique_visitors": 300
    }
  ],
  "daily_pageviews": [
    {
      "date": "2024-01-01",
      "count": 50
    }
  ],
  "traffic_sources": [...],
  "device_breakdown": [...],
  "browser_breakdown": [...]
}
```

## Error Handling

### Standard Error Response

```typescript
{
  "error": "Error message",
  "details": "Additional details" // Optional
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (backend not running)

### Error Handling Pattern

```typescript
try {
  const data = await apiRequest('/api/contacts/submit/', {
    method: 'POST',
    body: JSON.stringify(formData),
  });
  // Handle success
} catch (error) {
  if (error.message.includes('429')) {
    // Rate limit exceeded
    showError('Too many requests. Please try again later.');
  } else if (error.message.includes('400')) {
    // Validation error
    showError('Please check your input and try again.');
  } else if (error.message.includes('503')) {
    // Backend unavailable
    showError('Service temporarily unavailable. Please try again later.');
  } else {
    // Other error
    showError('An error occurred. Please try again.');
  }
}
```

## Code Examples

### Contact Form Integration

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
      setError(err instanceof Error ? err.message : 'Failed to submit form');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Thank you for your submission!</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

### Waitlist Integration

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
      setError(err instanceof Error ? err.message : 'Failed to join waitlist');
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

### Analytics Tracking

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
    // Silently fail - analytics shouldn't break the app
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

### Dashboard Stats Hook

```typescript
// hooks/use-dashboard-stats.ts
import { useState, useEffect } from 'react';
import { apiRequest } from '@/lib/api-client';
import { getAuthToken } from '@/lib/auth';

interface DashboardStats {
  contacts: {
    total: number;
    new: number;
    pending: number;
    trend: number;
  };
  waitlist: {
    total: number;
    pending: number;
    avgScore: number;
    trend: number;
  };
  leads: {
    total: number;
    qualified: number;
    conversionRate: number;
    trend: number;
  };
  newsletter: {
    total: number;
    active: number;
    unsubscribes: number;
    growthRate: number;
  };
}

export function useDashboardStats(site?: string) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const endpoint = site 
          ? `/api/dashboard/stats/?site=${site}`
          : '/api/dashboard/stats/';
        
        const data = await apiRequest<DashboardStats>(endpoint, {
          headers: {
            'Authorization': `Basic ${getAuthToken()}`,
          },
        });
        
        setStats(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [site]);

  return { stats, loading, error };
}
```

## Best Practices

### 1. Always Handle Errors

```typescript
try {
  const data = await apiRequest('/api/endpoint/');
  // Handle success
} catch (error) {
  // Always handle errors gracefully
  console.error('API Error:', error);
  // Show user-friendly message
}
```

### 2. Use Loading States

```typescript
const [loading, setLoading] = useState(false);

// Set loading before request
setLoading(true);
try {
  await apiRequest('/api/endpoint/');
} finally {
  setLoading(false); // Always reset loading
}
```

### 3. Validate Input Client-Side

```typescript
// Validate before sending
if (!email || !isValidEmail(email)) {
  setError('Please enter a valid email address');
  return;
}
```

### 4. Respect Rate Limits

```typescript
// Handle 429 errors gracefully
if (error.message.includes('429')) {
  // Show message and disable form temporarily
  setError('Too many requests. Please wait a moment.');
  setTimeout(() => setError(null), 60000); // Clear after 1 minute
}
```

### 5. Use Environment Variables

```typescript
// Always use environment variables for API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### 6. Implement Retry Logic for Critical Operations

```typescript
async function apiRequestWithRetry(endpoint: string, options: RequestInit, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await apiRequest(endpoint, options);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // Exponential backoff
    }
  }
}
```

## Testing Integration

### Test Checklist

- [ ] Contact form submission works
- [ ] Waitlist join works
- [ ] Email verification works
- [ ] Analytics tracking works
- [ ] Error handling works
- [ ] Loading states work
- [ ] Multi-site detection works
- [ ] Authentication works for admin endpoints

### Test Script

```typescript
// test-integration.ts
async function testIntegration() {
  // Test contact form
  try {
    const contactResponse = await apiRequest('/api/contacts/submit/', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Test User',
        email: 'test@example.com',
        subject: 'Test',
        message: 'Test message',
      }),
    });
    console.log('✓ Contact form works');
  } catch (error) {
    console.error('✗ Contact form failed:', error);
  }

  // Test waitlist
  try {
    const waitlistResponse = await apiRequest('/api/waitlist/join/', {
      method: 'POST',
      body: JSON.stringify({
        email: 'test@example.com',
      }),
    });
    console.log('✓ Waitlist join works');
  } catch (error) {
    console.error('✗ Waitlist join failed:', error);
  }

  // Test analytics
  try {
    const analyticsResponse = await apiRequest('/api/analytics/pageview/', {
      method: 'POST',
      body: JSON.stringify({
        page_url: 'https://example.com/test',
        page_title: 'Test Page',
      }),
    });
    console.log('✓ Analytics tracking works');
  } catch (error) {
    console.error('✗ Analytics tracking failed:', error);
  }
}
```

## Support

For issues or questions:
1. Check the API documentation at `/api/docs/` (Swagger UI)
2. Check the ReDoc documentation at `/api/redoc/`
3. Review error messages in the response
4. Check backend logs for detailed error information

