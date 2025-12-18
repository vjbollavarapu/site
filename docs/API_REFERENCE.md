# API Reference

Complete reference for all API endpoints in the backend.

## Base URL

- Development: `http://localhost:8000`
- Production: Set via `NEXT_PUBLIC_API_URL` environment variable

## Authentication

### Admin Endpoints

Require Basic Authentication:

```http
Authorization: Basic base64(username:password)
```

### Public Endpoints

No authentication required. Rate limiting may apply.

## Endpoints

### Contacts

#### `POST /api/contacts/submit/`

Submit a contact form (Public).

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry",
  "message": "Message content (min 10, max 10000 chars)",
  "phone": "+1234567890",
  "company": "Company Name",
  "recaptcha_token": "token"
}
```

**Response (201):**
```json
{
  "success": true,
  "submission_id": "uuid",
  "message": "Thank you for your submission."
}
```

**Rate Limit:** 5 requests per IP per hour

#### `GET /api/contacts/`

List contacts (Admin).

**Query Parameters:**
- `site` - Filter by site name or ID
- `status` - Filter by status (new, contacted, resolved, archived)
- `search` - Search by name or email
- `page` - Page number
- `page_size` - Items per page

**Response (200):**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "John Doe",
      "email": "john@example.com",
      "subject": "Inquiry",
      "message": "Message content",
      "status": "new",
      "priority": "medium",
      "site": {
        "id": "uuid",
        "name": "oasys360",
        "domain": "oasys360.com"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 100,
  "next": "url",
  "previous": null
}
```

#### `GET /api/contacts/:id/`

Get contact details (Admin).

**Response (200):**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry",
  "message": "Message content",
  "status": "new",
  "priority": "medium",
  "site": {...},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### `PATCH /api/contacts/:id/`

Update contact (Admin).

**Request:**
```json
{
  "status": "contacted",
  "priority": "high"
}
```

#### `DELETE /api/contacts/:id/`

Delete contact (Admin).

**Response (204):** No content

### Waitlist

#### `POST /api/waitlist/join/`

Join waitlist (Public).

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "company": "Company Name",
  "role": "CEO",
  "company_size": "51-200",
  "industry": "technology",
  "use_case": "Description",
  "ab_test_name": "landing_page_variant"
}
```

**Response (201):**
```json
{
  "success": true,
  "entry_id": "uuid",
  "message": "Please check your email to verify your subscription."
}
```

**Rate Limit:** 10 requests per IP per hour (configurable)

#### `POST /api/waitlist/verify/`

Verify waitlist email (Public).

**Request:**
```json
{
  "token": "verification-token"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Your email has been verified!"
}
```

#### `GET /api/waitlist/status/:email/`

Check waitlist status (Public).

**Response (200):**
```json
{
  "email": "user@example.com",
  "status": "pending",
  "priority_score": 75,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### `GET /api/waitlist/entries/`

List waitlist entries (Admin).

**Query Parameters:**
- `site` - Filter by site
- `status` - Filter by status
- `search` - Search by email or name
- `verified` - Filter by verification status

### Leads

#### `POST /api/leads/capture/`

Capture lead (Public).

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "company": "Company Name",
  "industry": "technology",
  "job_title": "CEO",
  "company_size": "51-200",
  "ab_test_name": "lead_form_variant"
}
```

**Response (201):**
```json
{
  "success": true,
  "lead_id": "uuid",
  "message": "Lead captured successfully."
}
```

#### `GET /api/leads/`

List leads (Admin).

**Query Parameters:**
- `site` - Filter by site
- `status` - Filter by status
- `search` - Search by name or email

### Newsletter

#### `POST /api/newsletter/subscribe/`

Subscribe to newsletter (Public).

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "preference": "weekly",
  "interests": ["tech", "healthcare"],
  "source": "website"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Please check your email to verify your subscription."
}
```

#### `POST /api/newsletter/verify/`

Verify newsletter subscription (Public).

**Request:**
```json
{
  "token": "verification-token"
}
```

#### `POST /api/newsletter/unsubscribe/`

Unsubscribe from newsletter (Public).

**Request:**
```json
{
  "email": "user@example.com",
  "token": "unsubscribe-token",
  "reason": "Too many emails"
}
```

#### `GET /api/newsletter/subscribers/`

List subscribers (Admin).

**Query Parameters:**
- `site` - Filter by site
- `status` - Filter by status (subscribed, unsubscribed, bounced)
- `search` - Search by email or name
- `verified` - Filter by verification status

#### `GET /api/newsletter/subscribers/stats/`

Get newsletter statistics (Admin).

**Response (200):**
```json
{
  "total_subscribers": 1000,
  "subscription_growth_last_30_days": 50,
  "unsubscribe_rate": 2.5,
  "bounce_rate": 1.0,
  "by_status": {
    "subscribed": 950,
    "unsubscribed": 40,
    "bounced": 10
  },
  "by_preference": {
    "weekly": 800,
    "monthly": 150
  }
}
```

### Analytics

#### `POST /api/analytics/pageview/`

Track page view (Public).

**Request:**
```json
{
  "page_url": "https://example.com/page",
  "page_title": "Page Title",
  "referrer_url": "https://google.com",
  "duration": 45.5,
  "session_id": "session-id"
}
```

**Response (201):**
```json
{
  "success": true,
  "session_id": "session-id",
  "pageview_id": "uuid"
}
```

**Rate Limit:** 10 requests per IP per hour

#### `POST /api/analytics/event/`

Track event (Public).

**Request:**
```json
{
  "event_name": "button_click",
  "event_category": "user_interaction",
  "event_value": 10.5,
  "event_properties": {
    "button_id": "cta-primary"
  },
  "page_url": "https://example.com/page",
  "session_id": "session-id"
}
```

**Response (201):**
```json
{
  "success": true,
  "event_id": "uuid",
  "session_id": "session-id"
}
```

**Rate Limit:** 10 requests per IP per hour

#### `GET /api/analytics/dashboard/`

Get analytics dashboard (Admin).

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)
- `site` - Filter by site

**Response (200):**
```json
{
  "overview": {
    "total_pageviews": 10000,
    "unique_visitors": 5000,
    "avg_session_duration": 120.5,
    "bounce_rate": 45.2
  },
  "top_pages": [
    {
      "page_url": "/",
      "page_title": "Home",
      "views": 5000,
      "unique_visitors": 3000
    }
  ],
  "daily_pageviews": [
    {
      "date": "2024-01-01",
      "count": 500
    }
  ],
  "traffic_sources": [...],
  "device_breakdown": [...],
  "browser_breakdown": [...]
}
```

### Dashboard

#### `GET /api/dashboard/stats/`

Get dashboard statistics (Admin).

**Query Parameters:**
- `site` - Filter by site name or ID

**Response (200):**
```json
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
  "site": {
    "id": "uuid",
    "name": "oasys360",
    "domain": "oasys360.com",
    "display_name": "Oasys360"
  }
}
```

## Error Responses

### Standard Error Format

```json
{
  "error": "Error message",
  "details": "Additional details"
}
```

### Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

### Validation Errors

```json
{
  "email": ["This field is required."],
  "message": ["This field must be at least 10 characters."]
}
```

## Rate Limiting

Rate limits are applied per IP address:

- Contact form: 5 requests/hour
- Waitlist join: 10 requests/hour (configurable)
- Analytics: 10 requests/hour per endpoint

Rate limit exceeded response (429):
```json
{
  "error": "Too many requests. Please try again later."
}
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Response:**
```json
{
  "results": [...],
  "count": 100,
  "next": "http://api.example.com/api/endpoint/?page=2",
  "previous": null
}
```

## Filtering

Most list endpoints support filtering:

**Query Parameters:**
- `site` - Filter by site name or ID
- `status` - Filter by status
- `search` - Search query
- `date_from` - Start date
- `date_to` - End date

**Example:**
```
GET /api/contacts/?site=oasys360&status=new&search=john
```

## Sorting

Some endpoints support sorting:

**Query Parameters:**
- `ordering` - Field to sort by (prefix with `-` for descending)

**Example:**
```
GET /api/contacts/?ordering=-created_at
```

