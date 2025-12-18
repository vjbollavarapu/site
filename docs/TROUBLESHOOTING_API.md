# API Integration Troubleshooting Guide

## Common Errors and Solutions

### Error: "Failed to fetch contacts"

This error typically occurs due to one of the following reasons:

#### 1. Backend Not Running

**Symptoms:**
- Error: "Cannot connect to backend API at http://localhost:8000"
- Network tab shows connection refused

**Solution:**
```bash
# Start the Django backend
cd apps/backend
source venv/bin/activate
python manage.py runserver
```

**Verify:**
```bash
curl http://localhost:8000/health/
# Should return: {"status": "ok"}
```

#### 2. Authentication Required

**Symptoms:**
- Error: "Authentication required" or 401/403 status
- Backend endpoint requires `IsAuthenticated` and `IsAdminUser`

**Solution:**

The contacts endpoint (`/api/contacts/`) requires admin authentication. You have two options:

**Option A: Add Authentication to Frontend (Recommended)**

1. Create an authentication helper:
```typescript
// lib/auth.ts
export function getAuthToken(): string | null {
  // Get from localStorage, cookies, or session
  return localStorage.getItem('auth_token')
}
```

2. Update API routes to include auth:
```typescript
// app/api/contacts/route.ts
const authToken = getAuthToken()
if (authToken) {
  headers['Authorization'] = `Basic ${authToken}`
}
```

**Option B: Use Django Admin Session (Development)**

1. Log in to Django admin: http://localhost:8000/admin/
2. The session cookie will be used automatically
3. Or use Basic Auth with admin credentials

**Option C: Temporarily Allow Unauthenticated Access (Development Only)**

⚠️ **Not recommended for production!**

Modify `apps/backend/apps/contacts/views.py`:
```python
class ContactSubmissionViewSet(viewsets.ModelViewSet):
    # Temporarily allow unauthenticated for development
    permission_classes = [AllowAny]  # Change from [IsAuthenticated, IsAdminUser]
```

#### 3. CORS Errors

**Symptoms:**
- Error: "CORS policy blocked"
- Network tab shows CORS error

**Solution:**

Check `apps/backend/.env.local`:
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

Verify in `apps/backend/sitebackend/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]
```

#### 4. Backend Endpoint Not Found (404)

**Symptoms:**
- Error: 404 Not Found
- Network tab shows 404 status

**Solution:**

1. Verify backend URL:
```bash
curl http://localhost:8000/api/contacts/
```

2. Check if endpoint exists:
```bash
# List all API endpoints
curl http://localhost:8000/api/schema/
```

3. Verify URL configuration in `apps/backend/sitebackend/urls.py`

#### 5. Database Not Migrated

**Symptoms:**
- Error: "relation does not exist"
- Backend logs show database errors

**Solution:**
```bash
cd apps/backend
python manage.py migrate
```

#### 6. Environment Variables Not Set

**Symptoms:**
- Connection errors
- Wrong API URL

**Solution:**

1. Create `apps/frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. Create `apps/backend/.env.local`:
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

3. Restart both servers after changing env vars

## Quick Diagnostic Steps

1. **Check Backend Health:**
   ```bash
   curl http://localhost:8000/health/
   ```

2. **Test Backend API Directly:**
   ```bash
   # Without auth (should fail with 401/403)
   curl http://localhost:8000/api/contacts/
   
   # With Basic Auth (replace user:pass with admin credentials)
   curl -u admin:password http://localhost:8000/api/contacts/
   ```

3. **Check Frontend API Route:**
   ```bash
   # From browser console or curl
   curl http://localhost:3000/api/contacts
   ```

4. **Check Browser Network Tab:**
   - Open DevTools → Network
   - Look for `/api/contacts` request
   - Check status code and response body
   - Look for CORS errors

5. **Check Backend Logs:**
   ```bash
   # In backend terminal, look for:
   # - Request logs
   # - Error messages
   # - Database errors
   ```

## Testing Authentication

### Test with Basic Auth

```bash
# Get base64 encoded credentials
echo -n "admin:password" | base64

# Use in API request
curl -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" \
     http://localhost:8000/api/contacts/
```

### Test with Session Auth

1. Log in to Django admin: http://localhost:8000/admin/
2. Copy session cookie from browser
3. Use in API request:
```bash
curl -H "Cookie: sessionid=your-session-id" \
     http://localhost:8000/api/contacts/
```

## Expected Behavior

### Without Authentication
- **Status:** 401 Unauthorized or 403 Forbidden
- **Response:** `{"detail": "Authentication credentials were not provided."}`

### With Authentication
- **Status:** 200 OK
- **Response:** `{"results": [...], "count": N}` or `[{...}, {...}]`

### Backend Not Running
- **Status:** 503 Service Unavailable (from Next.js API route)
- **Response:** `{"error": "Cannot connect to backend API..."}`

## Next Steps

1. **Implement Authentication:**
   - Add NextAuth.js or similar
   - Store tokens securely
   - Pass tokens in API requests

2. **Add Error Boundaries:**
   - Show user-friendly error messages
   - Provide retry options
   - Handle offline state

3. **Add Loading States:**
   - Show loading indicators
   - Disable buttons during requests
   - Provide feedback

---

**Last Updated:** 2024-12-19

