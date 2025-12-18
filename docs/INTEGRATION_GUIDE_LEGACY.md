# Frontend-Backend Integration Guide

This guide explains how the Next.js frontend integrates with the Django REST API backend in this monorepo.

## 🔌 API Connection

### Configuration

The frontend connects to the backend API through environment variables:

**Frontend** (`apps/frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`apps/backend/.env.local`):
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### API Client

The frontend API client is located at `apps/frontend/lib/api.ts`. It provides:

- Base URL configuration from environment variables
- Helper function `apiRequest()` for making authenticated requests
- Type-safe API calls

### Example Usage

```typescript
import { apiRequest } from '@/lib/api';

// GET request
const contacts = await apiRequest('/api/contacts/');

// POST request
const newContact = await apiRequest('/api/contacts/submit/', {
  method: 'POST',
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    subject: 'Inquiry',
    message: 'Hello',
  }),
});
```

## 🔐 Authentication

### Current Setup

The backend uses Django's session authentication and Basic Auth for API access.

### Frontend Authentication (To Be Implemented)

1. **Session-based Auth**: Use NextAuth.js or similar
2. **Token-based Auth**: Store JWT tokens in httpOnly cookies
3. **API Key**: For admin operations

### Example Implementation

```typescript
// apps/frontend/lib/auth.ts
export function getAuthToken(): string | null {
  // Retrieve token from cookies or localStorage
  return localStorage.getItem('auth_token');
}

// Update apiRequest to include token
const token = getAuthToken();
if (token) {
  config.headers = {
    ...config.headers,
    'Authorization': `Basic ${token}`,
  };
}
```

## 📡 API Endpoints

### Available Endpoints

All endpoints are documented in:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Postman Collection**: `apps/backend/API_POSTMAN_COLLECTION.json`

### Key Endpoints

#### Contacts
- `GET /api/contacts/` - List contacts (admin)
- `POST /api/contacts/submit/` - Submit contact form (public)
- `GET /api/contacts/:id/` - Get contact detail (admin)
- `PATCH /api/contacts/:id/` - Update contact (admin)

#### Waitlist
- `POST /api/waitlist/join/` - Join waitlist (public)
- `POST /api/waitlist/verify/` - Verify email (public)
- `GET /api/waitlist/status/:email/` - Check status (public)
- `GET /api/waitlist/entries/` - List entries (admin)

#### Leads
- `POST /api/leads/capture/` - Capture lead (public)
- `GET /api/leads/` - List leads (admin)
- `POST /api/leads/:id/qualify/` - Qualify lead (admin)
- `POST /api/leads/:id/convert/` - Convert lead (admin)

#### Newsletter
- `POST /api/newsletter/subscribe/` - Subscribe (public)
- `POST /api/newsletter/verify/` - Verify email (public)
- `GET /api/newsletter/subscribers/` - List subscribers (admin)

#### Analytics
- `POST /api/analytics/pageview/` - Track page view (public)
- `POST /api/analytics/event/` - Track event (public)
- `GET /api/analytics/dashboard/` - Dashboard data (admin)

#### GDPR
- `POST /api/gdpr/consent/` - Manage consent (public)
- `GET /api/gdpr/export/:email/` - Export data (public)
- `DELETE /api/gdpr/delete/:email/` - Delete data (public)

## 🎯 Integration Points

### 1. Dashboard Stats

**Frontend**: `apps/frontend/components/stats-cards.tsx`
**Backend**: Currently using mock data, needs endpoint: `/api/dashboard/stats/`

**To Implement**:
```python
# apps/backend/apps/core/api_views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    return Response({
        'contacts': {
            'total': ContactSubmission.objects.count(),
            'new': ContactSubmission.objects.filter(status='new').count(),
            # ...
        },
        # ...
    })
```

### 2. Data Tables

**Frontend**: Uses TanStack Table with API hooks
**Backend**: REST API endpoints with pagination

**Example**:
```typescript
// apps/frontend/hooks/use-contacts.ts
export function useContacts() {
  const { data, error } = useSWR('/api/contacts/', apiRequest);
  return { contacts: data, isLoading: !error && !data, error };
}
```

### 3. Form Submissions

**Frontend**: React Hook Form with Zod validation
**Backend**: Django REST Framework serializers

**Example**:
```typescript
// Frontend form submission
const onSubmit = async (data: FormData) => {
  await apiRequest('/api/contacts/submit/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
};
```

### 4. Real-time Updates

**Option 1**: Polling
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    refetch();
  }, 5000);
  return () => clearInterval(interval);
}, []);
```

**Option 2**: WebSockets (future)
- Use Django Channels
- Next.js WebSocket client

## 🐛 Error Handling

### Frontend Error Handling

```typescript
try {
  const data = await apiRequest('/api/endpoint/');
} catch (error) {
  if (error.message.includes('429')) {
    // Rate limit error
    toast.error('Too many requests. Please try again later.');
  } else if (error.message.includes('401')) {
    // Unauthorized
    redirect('/login');
  } else {
    // Generic error
    toast.error('An error occurred. Please try again.');
  }
}
```

### Backend Error Responses

The backend returns standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## 🔄 Data Flow

### Example: Contact Form Submission

1. **User fills form** → Frontend validates with Zod
2. **Submit** → `POST /api/contacts/submit/`
3. **Backend validates** → Django serializer validation
4. **Save to database** → Create ContactSubmission record
5. **Send email** → Celery task (async)
6. **Return response** → `201 Created` with contact data
7. **Frontend updates** → Show success message, reset form

### Example: Admin Dashboard

1. **Load page** → Frontend fetches multiple endpoints
2. **Parallel requests**:
   - `GET /api/contacts/` → Contacts list
   - `GET /api/waitlist/entries/` → Waitlist entries
   - `GET /api/leads/` → Leads list
   - `GET /api/newsletter/subscribers/` → Subscribers
3. **Display data** → Render in tables, charts, cards

## 🧪 Testing Integration

### Manual Testing

1. Start backend: `npm run dev:backend`
2. Start frontend: `npm run dev:frontend`
3. Open browser: http://localhost:3000
4. Check network tab for API calls

### Automated Testing

```typescript
// apps/frontend/__tests__/api.test.ts
describe('API Integration', () => {
  it('should fetch contacts', async () => {
    const contacts = await apiRequest('/api/contacts/');
    expect(contacts).toBeDefined();
  });
});
```

## 🚀 Production Deployment

### Environment Variables

**Frontend**:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Backend**:
```bash
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=api.yourdomain.com
```

### CORS Configuration

Update `apps/backend/sitebackend/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

### API Gateway (Optional)

For production, consider:
- Nginx reverse proxy
- API Gateway (AWS API Gateway, Kong, etc.)
- CDN for static assets

## 📝 Next Steps

1. **Implement Authentication**
   - Add NextAuth.js to frontend
   - Implement JWT tokens or session auth

2. **Add Real API Endpoints**
   - Dashboard stats endpoint
   - Chart data endpoint
   - Real-time updates

3. **Error Handling**
   - Global error boundary
   - Retry logic for failed requests
   - Offline support

4. **Performance**
   - Implement caching (React Query)
   - Optimize API responses
   - Add pagination everywhere

5. **Testing**
   - Integration tests
   - E2E tests (Playwright/Cypress)
   - API contract testing

---

**Last Updated**: 2024-01-XX

