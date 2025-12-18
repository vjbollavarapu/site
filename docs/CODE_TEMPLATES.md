# Code Templates

Ready-to-use code templates for common integration patterns. Copy and adapt these templates for your needs.

## API Client Template

```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiRequestOptions extends RequestInit {
  authToken?: string;
}

export async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authentication if provided
  if (options.authToken) {
    headers['Authorization'] = `Basic ${options.authToken}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: `HTTP error! status: ${response.status}`
      }));
      throw new Error(error.message || error.detail || `HTTP error! status: ${response.status}`);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return {} as T;
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

export { API_BASE_URL };
```

## Contact Form Template

```typescript
// components/contact-form.tsx
'use client';

import { useState } from 'react';
import { apiRequest } from '@/lib/api-client';

interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
  phone?: string;
  company?: string;
}

export function ContactForm() {
  const [formData, setFormData] = useState<ContactFormData>({
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
    setSuccess(false);

    try {
      const response = await apiRequest<{ success: boolean; message: string }>(
        '/api/contacts/submit/',
        {
          method: 'POST',
          body: JSON.stringify(formData),
        }
      );

      if (response.success) {
        setSuccess(true);
        setFormData({ name: '', email: '', subject: '', message: '' });
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit form';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
        />
      </div>

      <div>
        <label htmlFor="subject">Subject</label>
        <input
          id="subject"
          type="text"
          value={formData.subject}
          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
          required
        />
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          value={formData.message}
          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
          required
          minLength={10}
          rows={5}
        />
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message" role="alert">
          Thank you for your submission! We'll get back to you soon.
        </div>
      )}

      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

## Waitlist Form Template

```typescript
// components/waitlist-form.tsx
'use client';

import { useState } from 'react';
import { apiRequest } from '@/lib/api-client';

export function WaitlistForm() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await apiRequest<{ success: boolean; message: string }>(
        '/api/waitlist/join/',
        {
          method: 'POST',
          body: JSON.stringify({ email, name: name || undefined }),
        }
      );

      if (response.success) {
        setSuccess(true);
        setEmail('');
        setName('');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to join waitlist';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name">Name (Optional)</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Your name"
        />
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
        />
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message" role="alert">
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

## Lead Capture Form Template

```typescript
// components/lead-capture-form.tsx
'use client';

import { useState } from 'react';
import { apiRequest } from '@/lib/api-client';

interface LeadFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
}

export function LeadCaptureForm() {
  const [formData, setFormData] = useState<LeadFormData>({
    first_name: '',
    last_name: '',
    email: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiRequest<{ success: boolean; message: string }>(
        '/api/leads/capture/',
        {
          method: 'POST',
          body: JSON.stringify(formData),
        }
      );

      if (response.success) {
        setSuccess(true);
        setFormData({ first_name: '', last_name: '', email: '' });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to capture lead');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Get Started'}
      </button>
    </form>
  );
}
```

## Newsletter Subscription Template

```typescript
// components/newsletter-form.tsx
'use client';

import { useState } from 'react';
import { apiRequest } from '@/lib/api-client';

export function NewsletterForm() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiRequest<{ success: boolean; message: string }>(
        '/api/newsletter/subscribe/',
        {
          method: 'POST',
          body: JSON.stringify({ email }),
        }
      );

      if (response.success) {
        setSuccess(true);
        setEmail('');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to subscribe');
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
      <button type="submit" disabled={loading}>
        {loading ? 'Subscribing...' : 'Subscribe'}
      </button>
    </form>
  );
}
```

## Analytics Tracking Template

```typescript
// lib/analytics.ts
import { apiRequest } from './api-client';

let sessionId: string | null = null;

function getSessionId(): string {
  if (typeof window === 'undefined') return '';
  
  if (!sessionId) {
    sessionId = localStorage.getItem('analytics_session_id') || 
                `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('analytics_session_id', sessionId);
  }
  return sessionId;
}

export async function trackPageView(
  pageUrl: string,
  pageTitle?: string,
  duration?: number
) {
  try {
    await apiRequest('/api/analytics/pageview/', {
      method: 'POST',
      body: JSON.stringify({
        page_url: pageUrl,
        page_title: pageTitle || (typeof document !== 'undefined' ? document.title : ''),
        session_id: getSessionId(),
        duration: duration,
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
  properties?: Record<string, any>,
  value?: number
) {
  try {
    await apiRequest('/api/analytics/event/', {
      method: 'POST',
      body: JSON.stringify({
        event_name: eventName,
        event_category: category,
        event_value: value,
        event_properties: properties || {},
        session_id: getSessionId(),
        page_url: typeof window !== 'undefined' ? window.location.href : '',
      }),
    });
  } catch (error) {
    console.error('Event tracking failed:', error);
  }
}

// Helper functions for common events
export const trackButtonClick = (buttonId: string, page?: string) => {
  trackEvent('button_click', 'user_interaction', {
    button_id: buttonId,
    page: page || (typeof window !== 'undefined' ? window.location.pathname : ''),
  });
};

export const trackFormSubmit = (formId: string, formType: string) => {
  trackEvent('form_submit', 'conversion', {
    form_id: formId,
    form_type: formType,
  });
};

export const trackDownload = (fileName: string, fileType: string) => {
  trackEvent('download', 'engagement', {
    file_name: fileName,
    file_type: fileType,
  });
};
```

## Analytics Hook Template

```typescript
// hooks/use-analytics.ts
'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { trackPageView } from '@/lib/analytics';

export function usePageViewTracking() {
  const pathname = usePathname();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      trackPageView(window.location.href, document.title);
    }
  }, [pathname]);
}
```

## Dashboard Stats Hook Template

```typescript
// hooks/use-dashboard-stats.ts
'use client';

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
  site?: {
    id: string;
    name: string;
    domain: string;
    display_name: string;
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
        setError(null);
        
        const endpoint = site 
          ? `/api/dashboard/stats/?site=${site}`
          : '/api/dashboard/stats/';
        
        const token = getAuthToken();
        const data = await apiRequest<DashboardStats>(endpoint, {
          headers: {
            ...(token ? { 'Authorization': `Basic ${token}` } : {}),
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

  return { stats, loading, error, refetch: () => {
    // Trigger refetch by updating dependency
    setStats(null);
    setLoading(true);
  } };
}
```

## Error Boundary Template

```typescript
// components/error-boundary.tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Retry Logic Template

```typescript
// lib/retry.ts
export async function retryRequest<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error | null = null;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      // Don't retry on client errors (4xx)
      if (error instanceof Error && error.message.includes('40')) {
        throw error;
      }

      // Exponential backoff
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }

  throw lastError || new Error('Request failed after retries');
}

// Usage
const data = await retryRequest(() => 
  apiRequest('/api/contacts/submit/', {
    method: 'POST',
    body: JSON.stringify(formData),
  })
);
```

## Site Detection Template

```typescript
// lib/site-detection.ts
const SITE_MAP: Record<string, string> = {
  'oasys360.com': 'oasys360',
  'heals360.com': 'heals360',
  'reliqo.app': 'reliqo',
  'vcsmy.com': 'vcsmy',
};

export function getCurrentSite(): string | null {
  if (typeof window === 'undefined') return null;
  
  const hostname = window.location.hostname;
  
  // Check exact match
  if (SITE_MAP[hostname]) {
    return SITE_MAP[hostname];
  }
  
  // Check partial match (for www, subdomains)
  for (const [domain, site] of Object.entries(SITE_MAP)) {
    if (hostname.includes(domain)) {
      return site;
    }
  }
  
  return null;
}

export function getSiteConfig(site: string) {
  const configs: Record<string, any> = {
    oasys360: { name: 'Oasys360', theme: 'blue' },
    heals360: { name: 'Heals360', theme: 'green' },
    reliqo: { name: 'Reliqo', theme: 'purple' },
    vcsmy: { name: 'VCSMY', theme: 'orange' },
  };
  
  return configs[site] || null;
}
```

## Usage Examples

### Using Templates

1. **Copy the template** you need
2. **Adapt to your UI framework** (React, Vue, etc.)
3. **Add your styling** (Tailwind, CSS modules, etc.)
4. **Test thoroughly**

### Example: Contact Form with Tailwind

```typescript
// Just add Tailwind classes to the template
<form onSubmit={handleSubmit} className="space-y-4 max-w-md">
  <input
    className="w-full px-4 py-2 border rounded"
    // ... rest of props
  />
</form>
```

### Example: With Form Validation

```typescript
const [errors, setErrors] = useState<Record<string, string>>({});

const validate = () => {
  const newErrors: Record<string, string> = {};
  
  if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) {
    newErrors.email = 'Please enter a valid email';
  }
  
  if (formData.message.length < 10) {
    newErrors.message = 'Message must be at least 10 characters';
  }
  
  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!validate()) return;
  // ... rest of submit logic
};
```

## Notes

- All templates are TypeScript-ready
- Error handling is included
- Loading states are included
- Templates follow best practices
- Ready to use with Next.js, React, or any framework
- Adapt styling to your design system

