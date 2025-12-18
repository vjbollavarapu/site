# Frontend-Backend Integration Complete! 🎉

The frontend and backend have been successfully integrated. The Next.js frontend now connects to the Django REST API backend.

## ✅ What's Been Integrated

### 1. API Client Setup
- ✅ Created `lib/api-client.ts` - Server-side API client for Next.js API routes
- ✅ Created `lib/api.ts` - Client-side API utilities (for direct calls if needed)
- ✅ Environment variable configuration (`NEXT_PUBLIC_API_URL`)

### 2. API Routes Updated
- ✅ **Contacts**: `/api/contacts/` - List, get, update, delete
- ✅ **Contacts Bulk**: `/api/contacts/bulk-update/` - Bulk operations
- ✅ **Waitlist**: `/api/waitlist/entries/` - List waitlist entries
- ✅ **Leads**: `/api/leads/` - List leads

### 3. Backend Configuration
- ✅ CORS configured to allow frontend origin
- ✅ Environment variables set up
- ✅ API endpoints ready

## 🔄 How It Works

### Architecture

```
Frontend Component → Next.js API Route → Django Backend API
     (React)              (Proxy)            (Django REST)
```

1. **Frontend components** call Next.js API routes (e.g., `/api/contacts`)
2. **Next.js API routes** proxy requests to Django backend (e.g., `http://localhost:8000/api/contacts/`)
3. **Django backend** processes the request and returns data
4. **Next.js API route** transforms response and returns to frontend

### Example Flow

```typescript
// Frontend hook (use-contacts.ts)
const response = await fetch('/api/contacts?status=new')

// Next.js API route (app/api/contacts/route.ts)
const data = await apiRequest('/api/contacts/?status=new', { authToken })

// Django backend (apps/backend/apps/contacts/api_views.py)
@api_view(['GET'])
def list_contacts(request):
    return Response(contacts)
```

## 🧪 Testing the Integration

### 1. Start Both Servers

```bash
# Terminal 1: Backend
cd apps/backend
source venv/bin/activate
python manage.py runserver

# Terminal 2: Frontend
cd apps/frontend
pnpm dev
```

Or use the monorepo script:
```bash
npm run dev
```

### 2. Test API Connectivity

**Check Backend Health:**
```bash
curl http://localhost:8000/health/
```

**Check API Endpoint:**
```bash
curl http://localhost:8000/api/contacts/
```

**Test from Frontend:**
1. Open http://localhost:3000
2. Navigate to Contacts page
3. Check browser DevTools → Network tab
4. Look for requests to `/api/contacts`
5. Verify responses are coming from Django backend

### 3. Test Specific Endpoints

**Contacts:**
```bash
# List contacts
curl http://localhost:8000/api/contacts/

# Get specific contact (replace ID)
curl http://localhost:8000/api/contacts/{id}/
```

**Waitlist:**
```bash
# List waitlist entries
curl http://localhost:8000/api/waitlist/entries/
```

**Leads:**
```bash
# List leads
curl http://localhost:8000/api/leads/
```

## 🔧 Configuration

### Environment Variables

**Frontend** (`apps/frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`apps/backend/.env.local`):
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### CORS Settings

The backend automatically allows the frontend origin. If you need to add more origins, update `apps/backend/sitebackend/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://yourdomain.com',
]
```

## 📝 Remaining API Routes to Update

The following routes still need to be updated to connect to Django backend:

### Newsletter
- [ ] `/api/newsletter/subscribers/` - List subscribers
- [ ] `/api/newsletter/subscribers/[id]/` - Get/update subscriber
- [ ] `/api/newsletter/stats/` - Get stats
- [ ] `/api/newsletter/export/` - Export subscribers
- [ ] `/api/newsletter/import/` - Import subscribers

### Waitlist
- [ ] `/api/waitlist/entries/[id]/` - Get/update entry
- [ ] `/api/waitlist/status/[email]/` - Check status
- [ ] `/api/waitlist/verify/` - Verify email
- [ ] `/api/waitlist/bulk-update/` - Bulk operations

### Leads
- [ ] `/api/leads/[id]/` - Get/update lead
- [ ] `/api/leads/bulk-qualify/` - Bulk qualify
- [ ] `/api/leads/bulk-convert/` - Bulk convert

### Analytics
- [ ] `/api/analytics/dashboard/` - Dashboard data
- [ ] `/api/analytics/export/` - Export analytics

### GDPR
- [ ] `/api/gdpr/consent/` - Manage consent
- [ ] `/api/gdpr/export/[email]/` - Export data
- [ ] `/api/gdpr/access/[email]/` - Access data
- [ ] `/api/gdpr/delete/[email]/` - Delete data

## 🔐 Authentication

Currently, the API routes support Basic Auth via the `Authorization` header. To implement:

1. **Add authentication to frontend hooks:**
```typescript
// In hooks, add auth header
const response = await fetch('/api/contacts', {
  headers: {
    'Authorization': `Basic ${authToken}`,
  },
});
```

2. **Or implement session-based auth:**
- Use NextAuth.js
- Store tokens in httpOnly cookies
- Pass tokens via API routes

## 🐛 Troubleshooting

### CORS Errors

**Error**: `Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**:
1. Check `CORS_ALLOWED_ORIGINS` in backend `.env.local`
2. Verify backend is running
3. Check browser console for exact error

### 404 Errors

**Error**: `404 Not Found` when calling API routes

**Solution**:
1. Verify backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
3. Test backend endpoint directly: `curl http://localhost:8000/api/contacts/`

### 500 Errors

**Error**: `500 Internal Server Error`

**Solution**:
1. Check backend logs for errors
2. Verify database migrations are run: `python manage.py migrate`
3. Check backend `.env.local` configuration

### Empty Responses

**Issue**: API returns empty array `[]`

**Solution**:
1. Check if database has data
2. Verify API endpoint in Django admin
3. Check backend logs for errors

## 📚 Next Steps

1. **Update Remaining Routes**: Complete integration for newsletter, analytics, GDPR
2. **Add Authentication**: Implement proper auth flow
3. **Error Handling**: Add better error messages and retry logic
4. **Loading States**: Improve loading indicators
5. **Testing**: Write integration tests
6. **Documentation**: Update API documentation

## 🎯 Quick Reference

### Backend API Endpoints

- **Contacts**: `GET /api/contacts/`, `GET /api/contacts/{id}/`, `PATCH /api/contacts/{id}/`
- **Waitlist**: `GET /api/waitlist/entries/`, `POST /api/waitlist/join/`
- **Leads**: `GET /api/leads/`, `POST /api/leads/capture/`
- **Newsletter**: `GET /api/newsletter/subscribers/`, `POST /api/newsletter/subscribe/`
- **Analytics**: `GET /api/analytics/dashboard/`, `POST /api/analytics/pageview/`
- **GDPR**: `POST /api/gdpr/consent/`, `GET /api/gdpr/export/{email}/`

### Frontend API Routes

- **Contacts**: `/api/contacts`, `/api/contacts/[id]`, `/api/contacts/bulk-update`
- **Waitlist**: `/api/waitlist/entries`, `/api/waitlist/entries/[id]`
- **Leads**: `/api/leads`, `/api/leads/[id]`
- **Newsletter**: `/api/newsletter/subscribers`, `/api/newsletter/stats`

### API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Postman Collection**: `apps/backend/API_POSTMAN_COLLECTION.json`

---

**Integration Status**: ✅ Core routes integrated, remaining routes pending
**Last Updated**: 2024-12-19

