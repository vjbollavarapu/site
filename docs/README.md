# Documentation Index

Comprehensive documentation for the Site Backend monorepo project. This documentation is designed to be understood by AI assistants like Cursor.AI for automated integration and development.

## 📚 Getting Started

### 🚀 [Quick Start Guide](./QUICK_START.md)
Get up and running in minutes with basic integration examples.

**Read this first if you're:**
- New to the API
- Want to integrate quickly
- Need simple examples

### 📖 [Integration Guide](./INTEGRATION_GUIDE.md)
Comprehensive guide covering all aspects of integration.

**Covers:**
- API base configuration
- Authentication
- Multi-site support
- All API endpoints
- Error handling
- Code examples
- Best practices

### 📋 [API Reference](./API_REFERENCE.md)
Complete reference for all API endpoints.

**Includes:**
- Request/response formats
- Query parameters
- Status codes
- Error responses
- Rate limiting
- Pagination

### 📝 [Code Templates](./CODE_TEMPLATES.md)
Ready-to-use code templates for common integration patterns.

**Includes:**
- API client templates
- Form components
- Analytics tracking
- Hooks and utilities
- Error handling patterns

## 🌐 Multi-Site Support

### 🌍 [Multi-Site Integration](./MULTI_SITE_INTEGRATION.md)
Guide for integrating multiple websites/domains.

**Covers:**
- Site detection
- Filtering by site
- Site-specific configuration
- Best practices
- Troubleshooting

### ⚙️ [Multi-Site Setup](./MULTI_SITE_SETUP.md)
Setup instructions for multi-site support.

**Covers:**
- Site model setup
- Migration instructions
- CORS configuration
- Admin interface usage

## 🏗️ Project Setup

### 📦 [Monorepo Setup](./MONOREPO_SETUP.md)
Complete guide for setting up the monorepo structure.

**Covers:**
- Project structure
- Installation steps
- Environment configuration
- Docker setup
- Development workflow

### ✅ [Integration Complete](./INTEGRATION_COMPLETE.md)
Summary of completed frontend-backend integration.

**Covers:**
- What's been integrated
- How it works
- Testing instructions
- Remaining tasks

## 🚀 Deployment

### ✅ [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
Comprehensive checklist for production deployment.

**Covers:**
- Pre-deployment checks
- Environment configuration
- Database setup
- Security configuration
- Post-deployment verification

### 🏭 [Production Setup](./PRODUCTION_SETUP.md)
Step-by-step production deployment guide.

**Covers:**
- Server configuration
- Database setup
- Static files
- Email configuration
- Monitoring

### 📊 [Production Readiness](./PRODUCTION_READINESS.md)
Checklist for production readiness.

**Covers:**
- Security checklist
- Performance optimization
- Monitoring setup
- Backup strategy

### 🌐 [Nginx Production Setup](./NGINX_PRODUCTION_SETUP.md)
Nginx configuration for production.

**Covers:**
- Nginx configuration
- SSL setup
- Static file serving
- Reverse proxy configuration

## 🐛 Troubleshooting

### 🔧 [API Troubleshooting](./TROUBLESHOOTING_API.md)
Troubleshooting guide for API integration issues.

**Covers:**
- Common errors
- Connection issues
- Authentication problems
- CORS errors
- Rate limiting

### 📁 [Static Files Troubleshooting](./TROUBLESHOOT_STATIC_FILES.md)
Guide for troubleshooting static file issues.

**Covers:**
- Static file serving
- Nginx configuration
- WhiteNoise setup
- Common issues

### 📄 [Static Files Fix](./STATIC_FILES_FIX.md)
Quick fix guide for static file problems.

### 🔴 [Redis Troubleshooting](./REDIS_TROUBLESHOOTING.md)
Troubleshooting guide for Redis connection issues.

**Covers:**
- Connection errors
- Configuration
- Fallback options
- Best practices

## 🧪 Testing

### ✅ [Testing Guide](./README_TESTING.md)
Comprehensive testing documentation.

**Covers:**
- Test setup
- Running tests
- Test coverage
- Integration testing

## 🎨 UI/UX

### 🎨 [UI/UX Prompts](./UIUX_PROMPTS.md)
Prompts for generating UI/UX components with v0.dev.

**Covers:**
- Component prompts
- Design system guidelines
- API integration patterns
- Best practices

## 📖 Legacy Documentation

### 📘 [Legacy Integration Guide](./INTEGRATION_GUIDE_LEGACY.md)
Previous version of integration guide (kept for reference).

## Quick Links

### Essential Endpoints

**Public (No Auth Required):**
- `POST /api/contacts/submit/` - Submit contact form
- `POST /api/waitlist/join/` - Join waitlist
- `POST /api/waitlist/verify/` - Verify waitlist email
- `POST /api/leads/capture/` - Capture lead
- `POST /api/newsletter/subscribe/` - Subscribe to newsletter
- `POST /api/analytics/pageview/` - Track page view
- `POST /api/analytics/event/` - Track event

**Admin (Auth Required):**
- `GET /api/contacts/` - List contacts
- `GET /api/waitlist/entries/` - List waitlist entries
- `GET /api/leads/` - List leads
- `GET /api/newsletter/subscribers/` - List subscribers
- `GET /api/dashboard/stats/` - Dashboard statistics
- `GET /api/analytics/dashboard/` - Analytics dashboard

### Code Examples

**Contact Form:**
```typescript
await apiRequest('/api/contacts/submit/', {
  method: 'POST',
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    subject: 'Inquiry',
    message: 'Message content',
  }),
});
```

**Waitlist Join:**
```typescript
await apiRequest('/api/waitlist/join/', {
  method: 'POST',
  body: JSON.stringify({
    email: 'user@example.com',
  }),
});
```

**Analytics Tracking:**
```typescript
await apiRequest('/api/analytics/pageview/', {
  method: 'POST',
  body: JSON.stringify({
    page_url: window.location.href,
    page_title: document.title,
  }),
});
```

## Integration Checklist

Use this checklist when integrating:

- [ ] Set up API client with base URL
- [ ] Configure environment variables
- [ ] Implement contact form
- [ ] Implement waitlist form
- [ ] Set up analytics tracking
- [ ] Add error handling
- [ ] Add loading states
- [ ] Test from each website (multi-site)
- [ ] Implement authentication (for admin endpoints)
- [ ] Add retry logic for critical operations
- [ ] Test error scenarios
- [ ] Verify CORS configuration

## Supported Sites

The backend supports multiple websites:

- **Oasys360**: `oasys360` - https://oasys360.com
- **Heals360**: `heals360` - https://heals360.com
- **Reliqo**: `reliqo` - https://reliqo.app
- **VCSMY**: `vcsmy` - https://vcsmy.com

Site is automatically detected from the `Origin` header. See [Multi-Site Integration](./MULTI_SITE_INTEGRATION.md) for details.

## Authentication

### Public Endpoints
No authentication required. Rate limiting may apply.

### Admin Endpoints
Require Basic Authentication:

```typescript
headers: {
  'Authorization': `Basic ${btoa('username:password')}`
}
```

See [Integration Guide - Authentication](./INTEGRATION_GUIDE.md#authentication) for details.

## Error Handling

All endpoints return standard error format:

```json
{
  "error": "Error message",
  "details": "Additional details"
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `429` - Rate Limit Exceeded
- `500` - Server Error
- `503` - Service Unavailable

See [Integration Guide - Error Handling](./INTEGRATION_GUIDE.md#error-handling) for patterns.

## Rate Limiting

Rate limits applied per IP:
- Contact form: 5 requests/hour
- Waitlist join: 10 requests/hour
- Analytics: 10 requests/hour per endpoint

## Testing

### Test Backend Connection

```typescript
const testConnection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health/`);
    if (response.ok) {
      console.log('✓ Backend is running');
    }
  } catch (error) {
    console.error('✗ Backend is not accessible:', error);
  }
};
```

### Test API Endpoints

See [Quick Start Guide - Testing](./QUICK_START.md#testing) for test examples.

## Environment Variables

Required:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Optional:
```env
# For admin authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
```

## API Documentation

Interactive API documentation available:
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Support & Troubleshooting

### Common Issues

1. **CORS Errors**: Check `CORS_ALLOWED_ORIGINS` in backend settings
2. **503 Errors**: Backend not running - start with `python manage.py runserver`
3. **401 Errors**: Add authentication headers for admin endpoints
4. **429 Errors**: Rate limit exceeded - wait before retrying

### Getting Help

1. Check relevant documentation file
2. Review API documentation at `/api/docs/`
3. Check backend logs for detailed errors
4. Verify environment variables are set correctly

## Best Practices

1. **Always handle errors** - Don't let API errors break your app
2. **Use loading states** - Show feedback during API calls
3. **Validate input** - Validate client-side before sending
4. **Respect rate limits** - Handle 429 errors gracefully
5. **Use environment variables** - Never hardcode API URLs
6. **Implement retry logic** - For critical operations
7. **Track analytics** - Use provided analytics endpoints
8. **Test thoroughly** - Test from all supported sites

## Version History

- **v1.0** - Initial release with multi-site support
- Supports: Contacts, Waitlist, Leads, Newsletter, Analytics, Dashboard

## License

See main project LICENSE file.

---

**For AI Assistants (Cursor.AI, etc.):**

This documentation is structured to be easily parsed and understood by AI. When integrating:

1. Read `QUICK_START.md` for basic patterns
2. Reference `API_REFERENCE.md` for endpoint details
3. Use `INTEGRATION_GUIDE.md` for comprehensive examples
4. Check `MULTI_SITE_INTEGRATION.md` for multi-site patterns

All code examples are production-ready and can be directly used or adapted.

