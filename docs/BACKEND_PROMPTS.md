# Django Landing Page Backend - Complete Prompt Set for Cursor.AI

> Comprehensive prompts to build a standalone Django REST Framework backend that supports any landing page or marketing website with contact forms, waitlists, lead capture, and more.

---

## Table of Contents

1. [Project Setup & Architecture](#1-project-setup--architecture)
2. [Core Models & Database](#2-core-models--database)
3. [API Endpoints & Views](#3-api-endpoints--views)
4. [Security & Spam Protection](#4-security--spam-protection)
5. [Email Integration](#5-email-integration)
6. [CRM Integration](#6-crm-integration)
7. [Analytics & Tracking](#7-analytics--tracking)
8. [GDPR & Compliance](#8-gdpr--compliance)
9. [Admin Interface](#9-admin-interface)
10. [Testing & Documentation](#10-testing--documentation)
11. [Deployment & Configuration](#11-deployment--configuration)

---

## 1. Project Setup & Architecture

### Prompt 1.1: Initialize Django Project

```
Create or amend a project called "sitebackend" with the following structure:

- Use Django 4.2+ and Django REST Framework 3.14+
- Python 3.10+ virtual environment
- Project structure:
  sitebackend/
    ├── manage.py
    ├── sitebackend/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── apps/
    │   ├── contacts/
    │   ├── waitlist/
    │   ├── leads/
    │   ├── newsletter/
    │   ├── analytics/
    │   └── integrations/
    ├── requirements.txt
    ├── .env.example
    ├── README.md
    └── docker-compose.yml

Configure settings.py with:
- PostgreSQL database
- CORS enabled for frontend domains
- REST Framework with default authentication and pagination
- Timezone: UTC
- Language: en-us
- Static and media file handling
- Environment variables for sensitive data
```

### Prompt 1.2: Install Dependencies

```
Create requirements.txt with the following packages:

django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
celery==5.3.4
redis==5.0.1
django-filter==23.5
django-extensions==3.2.3
pillow==10.1.0
django-storages==1.14.2
boto3==1.29.7  # For S3 storage (optional)

# Email
django-ses==3.5.0  # AWS SES
sendgrid==6.11.0  # SendGrid alternative

# CRM Integration
requests==2.31.0
simple-salesforce==1.12.5  # Salesforce
hubspot-api-client==7.5.1  # HubSpot

# Security & Validation
django-ratelimit==4.1.0
django-honeypot==0.8.0
django-recaptcha==3.0.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
```

---

## 2. Core Models & Database

### Prompt 2.1: Contact Form Model

```
Create a Django app called "contacts" with a ContactSubmission model:

Features:
- UUID primary key
- Contact information: name, email, phone (optional), company (optional)
- Message fields: subject, message
- Metadata: source (website URL), referrer, user agent, IP address
- Status tracking: new, contacted, resolved, archived
- Priority levels: low, medium, high, urgent
- Assignment to team members
- Timestamps: created_at, updated_at, contacted_at, resolved_at
- Additional fields: custom_data (JSONField for flexible data storage)
- Spam detection: is_spam boolean, spam_score decimal
- GDPR: consent_given boolean, consent_timestamp

Add methods:
- mark_as_contacted()
- mark_as_resolved()
- mark_as_spam()

Create migration and add to admin.
```

### Prompt 2.2: Waitlist/Pilot Program Model

```
Create a Django app called "waitlist" with WaitlistEntry model:

Features:
- UUID primary key
- Email address (unique)
- Name (optional)
- Company (optional)
- Role/Job title (optional)
- Company size choices: 1-10, 11-50, 51-200, 201-1000, 1000+
- Industry choices: technology, finance, healthcare, retail, etc.
- Use case/Interest description (TextField)
- Source: website, referral, ad campaign, etc.
- Referral code (optional)
- Priority score (calculated field based on company size, role, etc.)
- Status: pending, approved, invited, onboarded, declined
- Invitation tracking: invited_at, invited_by, invite_code
- Timeline: expected_start_date
- Notes (internal)
- Timestamps: created_at, updated_at
- Email verification: is_verified, verified_at, verification_token
- Consent: marketing_consent, consent_timestamp

Add methods:
- approve()
- send_invitation()
- mark_onboarded()
- calculate_priority_score()

Create migration and add to admin.
```

### Prompt 2.3: Lead Capture Model

```
Create a Django app called "leads" with Lead model:

Features:
- UUID primary key
- Contact info: first_name, last_name, email, phone, company
- Lead source: organic, paid_ad, referral, social_media, email_campaign, etc.
- Lead score (calculated): 0-100 based on engagement
- Industry
- Job title/Role
- Company size
- Budget range
- Timeline (when looking to buy)
- Current solution
- Pain points (JSONField)
- Engagement tracking:
  - page_views (JSONField with timestamps)
  - downloads (JSONField)
  - webinar_registrations
  - demo_requests
- Status: new, contacted, qualified, unqualified, converted, lost
- Lifecycle stage: visitor, lead, marketing_qualified, sales_qualified, customer
- Assignment: assigned_to, assigned_at
- Tags (many-to-many)
- Custom fields (JSONField)
- Timestamps: created_at, updated_at, last_contacted_at, converted_at

Add methods:
- calculate_lead_score()
- qualify()
- convert()
- update_engagement()

Create migration and add to admin.
```

### Prompt 2.4: Newsletter Subscription Model

```
Create a Django app called "newsletter" with NewsletterSubscription model:

Features:
- UUID primary key
- Email (unique)
- Name (optional)
- Subscription status: subscribed, unsubscribed, bounced, complained
- Source: website, popup, footer, checkout, etc.
- Interests/Tags (JSONField or ManyToMany)
- Preference: daily, weekly, monthly
- Verification: is_verified, verified_at, verification_token
- Consent: consent_given, consent_timestamp, consent_text
- Unsubscribe: unsubscribed_at, unsubscribe_reason, unsubscribe_token
- Bounce tracking: bounce_count, last_bounce_at, bounce_reason
- Complaints: complaint_count, last_complaint_at
- Timestamps: created_at, updated_at
- Metadata: ip_address, user_agent, referrer

Add methods:
- subscribe()
- unsubscribe()
- verify()
- mark_bounced()
- mark_complained()

Create migration and add to admin.
```

### Prompt 2.5: Analytics & Event Tracking Model

```
Create a Django app called "analytics" with the following models:

1. PageView model:
   - UUID primary key
   - Session ID
   - Page URL
   - Page title
   - Referrer URL
   - User agent
   - IP address (hashed for GDPR)
   - Device type, browser, OS
   - Country, city (from IP geolocation)
   - Timestamp
   - Duration (time on page)
   - Exit page indicator

2. Event model:
   - UUID primary key
   - Event name (e.g., 'form_submit', 'button_click', 'video_play')
   - Event category
   - Event value (optional numeric)
   - Event properties (JSONField)
   - Session ID
   - Page URL
   - User identifier (optional)
   - Timestamp
   - Metadata

3. Conversion model:
   - UUID primary key
   - Conversion type (e.g., 'form_submission', 'signup', 'purchase')
   - Value (optional)
   - Lead/Contact reference
   - Attribution data (JSONField)
   - Campaign info
   - Timestamp

Create migrations and add to admin with filtering options.
```

---

## 3. API Endpoints & Views

### Prompt 3.1: Contact Form API

```
Create REST API endpoints for contact submissions:

Endpoints:
- POST /api/contacts/submit/ (public, no auth)
  - Accept: name, email, phone, company, subject, message, source, custom_data
  - Validate email format
  - Check for spam (basic heuristics)
  - Rate limiting: 5 submissions per IP per hour
  - Return: success message, submission ID
  
- GET /api/contacts/ (admin only)
  - List all submissions with filtering
  - Pagination: 20 per page
  - Filters: status, priority, date range, search
  
- GET /api/contacts/{id}/ (admin only)
  - Retrieve single submission
  
- PATCH /api/contacts/{id}/ (admin only)
  - Update status, priority, assign to user, add notes
  
- DELETE /api/contacts/{id}/ (admin only)
  - Soft delete (archive)

Create serializers:
- ContactSubmissionCreateSerializer (for public submission)
- ContactSubmissionSerializer (for admin)

Add validation:
- Email format
- Required fields
- Message length (max 5000 chars)
- Honeypot field (if enabled)
- reCAPTCHA validation (if enabled)

Add throttling:
- Use django-ratelimit
- 5 requests per IP per hour for public endpoint
```

### Prompt 3.2: Waitlist API

```
Create REST API endpoints for waitlist management:

Public Endpoints (no auth):
- POST /api/waitlist/join/
  - Accept: email, name, company, role, company_size, industry, use_case, source, referral_code
  - Validate email uniqueness
  - Create verification token
  - Send verification email
  - Return: success message, entry ID
  
- POST /api/waitlist/verify/
  - Accept: token
  - Verify email and mark as verified
  
- GET /api/waitlist/status/{email}/
  - Check waitlist status by email
  - Return: status, position (if applicable)

Admin Endpoints (auth required):
- GET /api/waitlist/entries/
  - List all entries with filtering
  - Pagination, sorting by priority_score
  - Filters: status, industry, company_size, date range
  
- GET /api/waitlist/entries/{id}/
  - Retrieve single entry
  
- PATCH /api/waitlist/entries/{id}/
  - Update status, add notes, assign
  
- POST /api/waitlist/entries/{id}/invite/
  - Send invitation email
  - Generate invite code
  
- GET /api/waitlist/stats/
  - Dashboard statistics:
    - Total entries
    - By status
    - By industry
    - By company size
    - Growth over time

Create serializers and add email verification flow.
```

### Prompt 3.3: Lead Capture API

```
Create REST API endpoints for lead management:

Public Endpoints:
- POST /api/leads/capture/
  - Accept: first_name, last_name, email, phone, company, source, industry, etc.
  - Calculate initial lead score
  - Check for duplicate leads
  - Return: lead ID, lead score
  
- POST /api/leads/{id}/track-event/
  - Track engagement events (page views, downloads, etc.)
  - Update lead score dynamically
  - Accept: event_name, event_properties

Admin Endpoints:
- GET /api/leads/
  - List with filtering, sorting, pagination
  - Filters: status, lifecycle_stage, score range, source, assigned_to
  
- GET /api/leads/{id}/
  - Detailed lead information
  - Include engagement history
  
- PATCH /api/leads/{id}/
  - Update lead information
  - Change status, lifecycle stage, assign
  
- POST /api/leads/{id}/qualify/
  - Mark as qualified
  - Update lifecycle stage
  
- POST /api/leads/{id}/convert/
  - Convert to customer
  - Record conversion event
  
- GET /api/leads/stats/
  - Lead pipeline statistics
  - Conversion rates
  - Source performance
  - Score distribution

Implement lead scoring algorithm based on:
- Company size
- Job title/role
- Engagement level
- Form completeness
- Website activity
```

### Prompt 3.4: Newsletter API

```
Create REST API endpoints for newsletter subscriptions:

Public Endpoints:
- POST /api/newsletter/subscribe/
  - Accept: email, name (optional), interests (optional), source
  - Validate email
  - Check if already subscribed
  - Create verification token
  - Send double opt-in email
  - Return: success message
  
- POST /api/newsletter/verify/
  - Accept: token
  - Verify subscription
  - Mark as verified
  
- POST /api/newsletter/unsubscribe/
  - Accept: email OR token
  - Unsubscribe from newsletter
  - Record reason (optional)
  - Return: confirmation

Admin Endpoints:
- GET /api/newsletter/subscribers/
  - List subscribers with filtering
  - Export to CSV functionality
  - Filters: status, interests, date range
  
- GET /api/newsletter/subscribers/{id}/
  - Subscriber details
  
- DELETE /api/newsletter/subscribers/{id}/
  - Delete subscriber (GDPR compliance)
  
- GET /api/newsletter/stats/
  - Total subscribers
  - Subscription growth
  - Unsubscribe rate
  - Bounce rate

Implement double opt-in flow and unsubscribe handling.
```

### Prompt 3.5: Analytics API

```
Create REST API endpoints for analytics:

Public Endpoints (tracking):
- POST /api/analytics/pageview/
  - Accept: page_url, page_title, referrer, session_id
  - Track page view
  - Extract device/browser info from user agent
  - Geolocation from IP (optional, anonymized)
  - Return: session_id
  
- POST /api/analytics/event/
  - Accept: event_name, event_category, event_value, properties, session_id, page_url
  - Track custom events
  - Return: event_id

Admin Endpoints:
- GET /api/analytics/dashboard/
  - Aggregate statistics:
    - Total page views
    - Unique visitors
    - Average session duration
    - Bounce rate
    - Top pages
    - Traffic sources
    - Device breakdown
    - Geographic data
  - Date range filtering
  
- GET /api/analytics/pageviews/
  - List page views with filtering
  - Pagination
  
- GET /api/analytics/events/
  - List events with filtering
  - Group by event name
  - Event value aggregations
  
- GET /api/analytics/conversions/
  - Conversion funnel
  - Conversion rate by source
  - Revenue attribution

Implement session tracking and aggregation queries.
```

---

## 4. Security & Spam Protection

### Prompt 4.1: Implement Security Features

```
Add comprehensive security features:

1. Rate Limiting:
   - Use django-ratelimit for all public endpoints
   - 5 requests per IP per hour for forms
   - 10 requests per IP per hour for analytics
   - Different limits for authenticated vs anonymous

2. Honeypot Protection:
   - Add hidden "website" field to forms
   - Reject submissions with honeypot filled
   - Use django-honeypot

3. reCAPTCHA Integration:
   - Add reCAPTCHA v3 to all public forms
   - Verify server-side
   - Score threshold: 0.5
   - Log low scores for review

4. Spam Detection:
   - Basic heuristics:
     - Suspicious keywords
     - Excessive links in message
     - ALL CAPS messages
     - Repeated characters
   - IP reputation (optional)
   - Email domain validation

5. Input Validation:
   - Sanitize all user inputs
   - Prevent XSS attacks
   - SQL injection protection (Django ORM handles this)
   - File upload validation (if applicable)

6. CORS Configuration:
   - Whitelist specific frontend domains
   - Configure in settings.py

7. IP Tracking (GDPR Compliant):
   - Hash IP addresses before storing
   - Use SHA-256 hashing
   - Store only last octet for analytics
```

### Prompt 4.2: Add Spam Detection Service

```
Create a spam detection service in apps/contacts/services.py:

Features:
- CheckSubmissionSpam class with methods:
  - check_honeypot() - verify honeypot field
  - check_recaptcha() - verify reCAPTCHA score
  - check_content() - analyze message content
  - check_rate_limit() - verify IP rate limit
  - calculate_spam_score() - return 0.0-1.0 score
  
- Spam indicators:
  - Suspicious keywords list
  - Link count threshold
  - Caps ratio
  - Repetitive patterns
  - Blacklisted domains/emails
  
- Auto-flag submissions with score > 0.7
- Log all spam attempts for analysis
```

---

## 5. Email Integration

### Prompt 5.1: Email Service Setup

```
Create email service in apps/integrations/email_service.py:

Support multiple providers:
- Django default (SMTP)
- AWS SES
- SendGrid
- Mailgun (optional)

Configuration via environment variables:
- EMAIL_BACKEND (django_ses.SESBackend, sendgrid_backend.SendgridBackend, etc.)
- Provider-specific credentials

Email templates:
- Contact form confirmation
- Waitlist verification
- Waitlist invitation
- Newsletter verification
- Newsletter welcome
- Newsletter unsubscribe confirmation

Template structure:
- HTML and plain text versions
- Use Django templates
- Store in apps/integrations/templates/emails/

Email sending:
- Use Celery for async sending (if enabled)
- Retry logic for failures
- Email queue management
- Bounce and complaint handling
```

### Prompt 5.2: Email Templates

```
Create email templates with the following structure:

1. Contact Form Confirmation:
   - Subject: "Thank you for contacting us"
   - Thank user
   - Include submission reference
   - Expected response time

2. Waitlist Verification:
   - Subject: "Verify your email - [Product Name] Waitlist"
   - Verification link with token
   - Instructions
   - Expires in 24 hours

3. Waitlist Invitation:
   - Subject: "You're in! Welcome to [Product Name]"
   - Invite code
   - Next steps
   - Onboarding link

4. Newsletter Verification:
   - Subject: "Confirm your subscription"
   - Double opt-in link
   - Unsubscribe link

5. Newsletter Welcome:
   - Subject: "Welcome to our newsletter!"
   - Welcome message
   - What to expect
   - Manage preferences link

Use Django template inheritance and make them responsive.
```

---

## 6. CRM Integration

### Prompt 6.1: CRM Service Abstraction

```
Create CRM integration service in apps/integrations/crm_service.py:

Support multiple CRM providers:
- HubSpot
- Salesforce
- Pipedrive
- Zoho CRM

Create abstract base class:
- CRMProvider abstract base class
- Methods:
  - create_contact()
  - update_contact()
  - create_lead()
  - create_deal()
  - create_note()
  - search_contact()

Implement for each provider:
- HubSpotCRMProvider
- SalesforceCRMProvider
- PipedriveCRMProvider

Configuration:
- Provider selection via environment variable
- Provider-specific credentials
- Field mapping configuration (JSON)

Auto-sync triggers:
- On contact submission
- On waitlist join
- On lead creation
- On status change

Error handling:
- Retry logic
- Queue failed syncs
- Log all sync attempts
```

### Prompt 6.2: HubSpot Integration

```
Implement HubSpot integration:

Features:
- Create contacts in HubSpot from form submissions
- Map fields: name → first_name/last_name, email, phone, company
- Create deals for qualified leads
- Add timeline notes for activities
- Update contact properties
- Tag contacts based on source

API Client:
- Use hubspot-api-client
- Handle rate limits
- Batch operations when possible

Configuration:
- HUBSPOT_API_KEY or HUBSPOT_ACCESS_TOKEN
- HUBSPOT_PORTAL_ID
- Field mapping JSON config

Sync strategy:
- Immediate sync for high-priority items
- Batch sync for others (via Celery)
- Retry on failure
```

---

## 7. Analytics & Tracking

### Prompt 7.1: Analytics Middleware

```
Create analytics middleware in apps/analytics/middleware.py:

Track:
- Page views automatically
- Session creation
- User journey tracking
- Conversion events
- Custom events

Features:
- Session management
- IP anonymization (GDPR)
- User agent parsing
- Referrer tracking
- Device detection
- Geolocation (optional, anonymized)

Storage:
- Store in database
- Optional: send to external analytics (Google Analytics, Mixpanel)
- Batch processing for performance

GDPR Compliance:
- Only track with consent
- Anonymize IP addresses
- Allow opt-out
```

### Prompt 7.2: Event Tracking Service

```
Create event tracking service in apps/analytics/services.py:

TrackEvents class:
- track_page_view()
- track_event()
- track_conversion()
- get_session()
- update_session()

Session handling:
- Create session ID (UUID)
- Store in cookie (30 days)
- Link events to sessions
- Calculate session duration
- Track session start/end

Event properties:
- Flexible JSONField for custom properties
- Standard properties: page_url, referrer, timestamp
- User identification (optional, hashed)

Aggregation:
- Pre-calculate common metrics
- Cache for dashboard performance
- Update stats in background jobs
```

---

## 8. GDPR & Compliance

### Prompt 8.1: GDPR Compliance Features

```
Implement GDPR compliance features:

1. Consent Management:
   - Consent model with:
     - consent_type (marketing, analytics, necessary)
     - consent_given (boolean)
     - consent_timestamp
     - consent_text (what they consented to)
     - ip_address (hashed)
     - withdrawal_timestamp

2. Data Export:
   - GET /api/gdpr/export/{email}/
   - Export all user data in JSON format
   - Include: contacts, waitlist, leads, newsletter, analytics
   - Anonymize sensitive data

3. Data Deletion:
   - DELETE /api/gdpr/delete/{email}/
   - Delete or anonymize all user data
   - Keep audit trail (optional)
   - Confirmation required

4. Right to Access:
   - GET /api/gdpr/access/{email}/
   - Return all data associated with email
   - JSON format

5. Consent Endpoints:
   - POST /api/gdpr/consent/
   - Accept/withdraw consent
   - Track consent history

6. Privacy Policy:
   - Store privacy policy versions
   - Link consent to policy version
   - Track policy acceptance

Implement data retention policies:
- Auto-delete old data after retention period
- Configurable per data type
```

### Prompt 8.2: Data Anonymization

```
Create data anonymization service in apps/integrations/anonymization_service.py:

Features:
- Anonymize personal data:
  - Email: hash or replace with "user@anonymous.com"
  - Name: replace with "Anonymous User"
  - Phone: remove or hash
  - IP: hash to last octet
  - Free text: remove PII patterns
  
- Anonymization methods:
  - Hash sensitive fields
  - Replace with generic values
  - Remove identifying information
  - Keep analytics data (anonymized)

- Anonymization triggers:
  - On GDPR deletion request
  - After retention period
  - Manual anonymization

- Audit trail:
  - Log all anonymizations
  - Keep anonymization timestamp
  - Reason for anonymization
```

---

## 9. Admin Interface

### Prompt 9.1: Django Admin Configuration

```
Configure Django admin for all models:

Features:
- List displays with key fields
- Search functionality
- Filters for status, date, source
- Custom actions:
  - Bulk approve/reject
  - Export to CSV
  - Send emails
  - Mark as spam
  
- Read-only fields where appropriate
- Inline editing for related models
- Custom admin views for statistics
- Date hierarchy
- Custom filters

Admin enhancements:
- django-admin-list-filter-dropdown for better UX
- django-import-export for bulk operations
- Custom admin dashboard with stats

Permissions:
- Different admin groups
- View-only permissions
- Edit permissions
- Export permissions
```

### Prompt 9.2: Admin Dashboard

```
Create custom admin dashboard:

Display:
- Today's submissions (contacts, waitlist, leads)
- Pending items count
- Conversion statistics
- Top sources
- Recent activity feed
- Quick actions

Charts:
- Submission trends (line chart)
- Source distribution (pie chart)
- Status breakdown (bar chart)
- Growth metrics

Use django-admin-tools or custom views.
```

---

## 10. Testing & Documentation

### Prompt 10.1: Unit Tests

```
Create comprehensive test suite:

Test coverage for:
- Models: creation, methods, constraints
- Views: GET, POST, PATCH, DELETE
- Serializers: validation, transformation
- Services: email, CRM, spam detection
- API endpoints: success and error cases
- Permissions: public vs admin
- Rate limiting
- Spam detection

Test files:
- apps/contacts/tests/
- apps/waitlist/tests/
- apps/leads/tests/
- apps/newsletter/tests/
- apps/analytics/tests/

Use:
- Django TestCase
- APIClient for API tests
- Factories (factory_boy) for test data
- Mock external services (email, CRM)

Target: 80%+ code coverage
```

### Prompt 10.2: API Documentation

```
Generate API documentation:

1. Use drf-yasg or drf-spectacular for Swagger/OpenAPI
2. Add docstrings to all views and serializers
3. Include:
   - Endpoint descriptions
   - Request/response examples
   - Error responses
   - Authentication requirements
   - Rate limits

4. Create README.md with:
   - Project overview
   - Setup instructions
   - API endpoint list
   - Environment variables
   - Deployment guide

5. Create API_POSTMAN_COLLECTION.json for Postman testing
```

---

## 11. Deployment & Configuration

### Prompt 11.1: Docker Configuration

```
Create Docker setup:

Files:
- Dockerfile (multi-stage build)
- docker-compose.yml:
  - Django app
  - PostgreSQL
  - Redis (for Celery, caching)
  - Nginx (optional, for production)
  
- .dockerignore
- docker-compose.prod.yml (production config)

Configuration:
- Environment variables in .env
- Database migrations on startup
- Collect static files
- Health checks
- Logging configuration
```

### Prompt 11.2: Environment Configuration

```
Create comprehensive .env.example:

Database:
- DATABASE_URL or individual DB settings
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

Email:
- EMAIL_BACKEND
- EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS
- EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- AWS_SES_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
- SENDGRID_API_KEY

CRM:
- CRM_PROVIDER (hubspot, salesforce, etc.)
- HUBSPOT_API_KEY
- SALESFORCE_* credentials

Security:
- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- CORS_ALLOWED_ORIGINS
- RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY

Analytics:
- GOOGLE_ANALYTICS_ID (optional)
- MIXPANEL_TOKEN (optional)

Other:
- REDIS_URL
- CELERY_BROKER_URL
- MEDIA_ROOT, STATIC_ROOT
- S3 settings (if using)
```

### Prompt 11.3: Deployment Checklist

```
Create deployment checklist:

Pre-deployment:
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Static files collected
- [ ] Security settings (DEBUG=False, SECRET_KEY)
- [ ] CORS configured
- [ ] Email service tested
- [ ] CRM integration tested
- [ ] Rate limiting configured
- [ ] Monitoring/logging setup

Deployment:
- [ ] Deploy to staging first
- [ ] Run migrations
- [ ] Collect static files
- [ ] Restart services
- [ ] Health check
- [ ] Smoke tests

Post-deployment:
- [ ] Monitor error logs
- [ ] Verify email sending
- [ ] Test form submissions
- [ ] Check analytics tracking
- [ ] Verify CRM sync
- [ ] Performance monitoring

Create deployment scripts:
- deploy.sh
- migrate.sh
- backup.sh
```

---

## Quick Start Prompt

```
I need a complete Django REST Framework backend for a landing page that handles:

1. Contact form submissions with spam protection
2. Waitlist/pilot program signups with email verification
3. Lead capture and scoring
4. Newsletter subscriptions with double opt-in
5. Analytics and event tracking
6. Email integration (AWS SES/SendGrid)
7. CRM integration (HubSpot/Salesforce)
8. GDPR compliance (consent, export, deletion)
9. Admin interface for managing submissions
10. API documentation

Start by creating the project structure, then implement each component following the detailed prompts above. Use PostgreSQL, Django 4.2+, DRF 3.14+, and include Docker setup.
```

---

## Additional Features (Optional)

### Prompt: Webhook Support

```
Add webhook functionality:
- Configurable webhook URLs per event type
- POST webhook on: contact submission, waitlist join, lead creation, conversion
- Retry logic for failed webhooks
- Webhook signature verification
- Webhook event history
- Test webhook endpoint
```

### Prompt: A/B Testing Support

```
Add A/B testing support:
- Track variant assignment
- Associate submissions with variants
- Conversion tracking by variant
- Statistical significance calculation
- Admin interface for managing tests
```

### Prompt: Multi-language Support

```
Add i18n support:
- Django i18n configuration
- Translation files for email templates
- API response translations
- Language detection from Accept-Language header
- Admin translations
```

---

**Usage Instructions:**

1. Use prompts sequentially (1.1 → 1.2 → 2.1 → 2.2, etc.)
2. Customize prompts based on your specific needs
3. Adjust model fields based on your landing page requirements
4. Add or remove features as needed
5. Test each component before moving to the next

**Note:** This is a comprehensive prompt set. You may not need all features immediately. Start with core functionality (contacts, waitlist) and expand as needed.

