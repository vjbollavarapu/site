# UI/UX Prompts for v0.dev

> Comprehensive prompts for generating modern, user-friendly UI components using v0.dev based on the Site Backend API.

## Table of Contents

1. [Public-Facing Pages](#public-facing-pages)
2. [Admin Dashboard Pages](#admin-dashboard-pages)
3. [Authentication & Verification](#authentication--verification)
4. [GDPR & Compliance](#gdpr--compliance)
5. [Analytics & Reporting](#analytics--reporting)
6. [Component Library](#component-library)

---

## Public-Facing Pages

### 1. Landing Page with Waitlist Join

**Prompt:**
```
Create a modern, conversion-optimized landing page with a waitlist signup form. The page should have:

Design:
- Hero section with large headline, subheadline, and primary CTA button
- Clean, modern design with gradient backgrounds or subtle animations
- Mobile-responsive layout
- Trust indicators (social proof, testimonials, or stats)
- Feature highlights section with icons
- Footer with newsletter signup and links

Waitlist Form Component:
- Form fields: email (required), name (optional), company (optional), role (optional), company_size (dropdown: 1-10, 11-50, 51-200, 201-1000, 1000+), industry (dropdown: technology, finance, healthcare, retail, education, etc.)
- Real-time email validation
- Loading state during submission
- Success message: "Check your email to verify your address"
- Error handling with user-friendly messages
- Rate limit error: "Too many requests. Please try again later."
- GDPR consent checkbox with link to privacy policy
- A/B testing support (variant A/B can be passed as prop)

API Integration:
- POST to /api/waitlist/join/ or /api/v1/marketing/early-access/
- Request body: { email, name?, company?, role?, company_size?, industry?, ab_test_name? }
- Handle 201 (success), 400 (validation error), 429 (rate limit), 500 (server error)

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- React Hook Form for form handling
- Zod for validation
- Shadcn/ui components
```

### 2. Contact Form Page

**Prompt:**
```
Create a professional contact form page with the following:

Design:
- Centered form layout with max-width container
- Clean, minimal design with proper spacing
- Form validation with inline error messages
- Success/error toast notifications
- Loading states on submit button

Form Fields:
- Name (required, text input)
- Email (required, email input with validation)
- Phone (optional, tel input)
- Company (optional, text input)
- Subject (required, text input)
- Message (required, textarea with character count)
- reCAPTCHA v3 integration (invisible)
- GDPR consent checkbox

Features:
- Real-time field validation
- Character count for message field (max 5000)
- Auto-save to localStorage (optional)
- Form submission animation
- Success message with estimated response time
- Error handling with retry option

API Integration:
- POST to /api/contacts/submit/
- Request body: { name, email, phone?, company?, subject, message }
- Handle rate limiting (5 per hour per IP)
- Show appropriate error messages

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- React Hook Form + Zod
- Shadcn/ui components (Button, Input, Textarea, Label, Checkbox)
- react-hot-toast for notifications
```

### 3. Newsletter Subscription Component

**Prompt:**
```
Create a newsletter subscription component that can be embedded in footer, sidebar, or as a popup modal:

Design:
- Compact, attractive design with email input and subscribe button
- Optional: Full-page modal with benefits list
- Success state with confirmation message
- Error handling with clear messages

Features:
- Email validation
- Loading state on button
- Success message: "Please check your email to verify your subscription"
- Unsubscribe link in footer
- GDPR consent checkbox

API Integration:
- POST to /api/newsletter/subscribe/
- Request body: { email, name?, source }
- Handle verification flow

Variants:
1. Footer component (horizontal layout)
2. Sidebar widget (vertical layout)
3. Popup modal (centered, with close button)
4. Inline section (full-width with benefits)

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- React Hook Form
```

### 4. Lead Capture Form

**Prompt:**
```
Create a lead capture form for gated content (ebooks, whitepapers, webinars):

Design:
- Two-column layout: form on left, content preview on right
- Progress indicator for multi-step forms
- Clean, professional design
- Mobile: stacked layout

Form Fields (Step 1):
- First Name (required)
- Last Name (required)
- Email (required)
- Company (optional)
- Lead Source (hidden, auto-detected or dropdown)

Form Fields (Step 2 - Optional):
- Industry (dropdown)
- Job Title (text)
- Company Size (dropdown)
- Phone (optional)

Features:
- Multi-step form with progress bar
- Form persistence across steps
- Success redirect to download/content page
- Lead scoring display (optional, admin view)
- Event tracking integration

API Integration:
- POST to /api/leads/capture/
- Request body: { first_name, last_name, email, company?, lead_source, industry?, job_title?, company_size?, phone? }
- Track conversion event after submission

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- React Hook Form with multi-step support
- Shadcn/ui components
- Framer Motion for transitions
```

---

## Admin Dashboard Pages

### 5. Admin Dashboard Overview

**Prompt:**
```
Create a comprehensive admin dashboard overview page with:

Layout:
- Sidebar navigation with collapsible menu
- Top header with user profile and notifications
- Main content area with cards and charts
- Responsive grid layout

Dashboard Cards:
1. Contacts Overview
   - Total contacts (with trend indicator)
   - New contacts (last 7 days)
   - Pending contacts count
   - Quick link to contacts list

2. Waitlist Overview
   - Total waitlist entries
   - Pending entries
   - Priority score average
   - Recent signups chart

3. Leads Overview
   - Total leads
   - Qualified leads count
   - Conversion rate
   - Lead score distribution

4. Newsletter Overview
   - Total subscribers
   - Active subscribers
   - Unsubscribes (last 30 days)
   - Growth rate

5. Analytics Overview
   - Total page views (last 30 days)
   - Unique visitors
   - Conversion rate
   - Top pages chart

Charts:
- Line chart: Contacts/Waitlist/Leads over time (last 30 days)
- Pie chart: Contact status distribution
- Bar chart: Lead sources
- Area chart: Newsletter growth

Quick Actions:
- Create new contact
- Approve waitlist entry
- Qualify lead
- Send newsletter

API Integration:
- Multiple API calls to fetch dashboard data
- Real-time updates (polling or WebSocket)
- Error handling with retry logic

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- Recharts or Chart.js for charts
- React Query for data fetching
- NextAuth for authentication
```

### 6. Contacts Management Page

**Prompt:**
```
Create a contacts management page for admins with:

Layout:
- Data table with sortable columns
- Filters sidebar (status, priority, date range, assigned to)
- Search bar with debounced input
- Bulk actions toolbar
- Pagination controls

Table Columns:
- Checkbox (for bulk selection)
- Name
- Email
- Company
- Subject (truncated)
- Status (badge with color coding)
- Priority (badge)
- Assigned To (avatar + name)
- Created At (relative time)
- Actions (view, edit, delete)

Features:
- Row click opens detail modal/sidebar
- Status filter chips (New, Contacted, Resolved, Archived)
- Priority filter (Low, Medium, High, Urgent)
- Date range picker
- Export to CSV button
- Bulk status update
- Bulk assign to user
- Real-time updates

Detail Modal/Sidebar:
- Full contact information
- Message preview
- Status timeline
- Notes section
- Activity log
- Quick actions (mark as contacted, resolve, archive)

API Integration:
- GET /api/contacts/ (with query params: status, priority, ordering, search)
- GET /api/contacts/:id/
- PATCH /api/contacts/:id/
- DELETE /api/contacts/:id/
- Handle pagination (page, page_size)

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components (Table, Dialog, Select, Input, Button)
- TanStack Table for advanced table features
- React Query for data fetching
- date-fns for date formatting
```

### 7. Waitlist Management Page

**Prompt:**
```
Create a waitlist management page with:

Layout:
- Kanban board view (Pending, Approved, Invited, Onboarded, Declined)
- List view toggle
- Filters and search
- Bulk actions

Kanban Cards:
- Email
- Name
- Company
- Priority Score (with visual indicator)
- Status badge
- Created date
- Quick actions (approve, decline, invite)

List View:
- Sortable table with columns: Email, Name, Company, Role, Company Size, Industry, Priority Score, Status, Created At
- Priority score highlighted (color-coded)
- Status filter chips
- Search by email, name, company

Features:
- Drag and drop between status columns (Kanban)
- Priority score visualization (progress bar or gauge)
- Bulk approve/decline
- Send invitation email (opens modal with template)
- Export to CSV
- Filter by company size, industry, source
- Sort by priority score, created date

Detail View:
- Full entry information
- Priority score breakdown
- Verification status
- Notes section
- Timeline (created, verified, approved, invited, onboarded)
- Quick actions

API Integration:
- GET /api/waitlist/entries/ (with filters and pagination)
- GET /api/waitlist/entries/:id/
- PATCH /api/waitlist/entries/:id/
- POST /api/waitlist/verify/ (for manual verification)

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- @dnd-kit/core for drag and drop
- TanStack Table
- React Query
```

### 8. Leads Management Page

**Prompt:**
```
Create a leads management page with CRM-like functionality:

Layout:
- List view with advanced filters
- Pipeline view (funnel visualization)
- Detail sidebar/modal
- Lead scoring visualization

List View:
- Table columns: Name, Email, Company, Lead Score (with progress bar), Status, Lifecycle Stage, Source, Assigned To, Created At
- Lead score color coding (0-30: red, 31-60: yellow, 61-100: green)
- Status badges
- Lifecycle stage indicators
- Quick qualify/convert buttons

Pipeline View:
- Funnel stages: New → Contacted → Qualified → Converted
- Cards showing lead count per stage
- Drag and drop to move between stages
- Visual flow with conversion rates

Filters:
- Status (New, Contacted, Qualified, Unqualified, Converted, Lost)
- Lifecycle Stage
- Lead Source
- Lead Score range (slider)
- Assigned To
- Date range
- Industry
- Company Size

Features:
- Lead scoring visualization (gauge chart)
- Bulk qualify/convert
- Assign to user
- Track events (button to add event)
- Notes and activity timeline
- Export to CSV
- Import from CSV

Detail View:
- Full lead information
- Lead score breakdown (with factors)
- Engagement timeline
- Events tracked
- Notes and comments
- Quick actions (qualify, convert, assign, add note)

API Integration:
- GET /api/leads/ (with filters)
- GET /api/leads/:id/
- PATCH /api/leads/:id/
- POST /api/leads/:id/qualify/
- POST /api/leads/:id/convert/
- POST /api/leads/:id/track-event/

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- Recharts for pipeline visualization
- TanStack Table
- React Query
```

### 9. Newsletter Management Page

**Prompt:**
```
Create a newsletter subscribers management page:

Layout:
- Subscribers table
- Subscription stats cards
- Filters and search
- Bulk actions

Stats Cards:
- Total Subscribers
- Active Subscribers
- Unsubscribed (last 30 days)
- Bounced
- Growth Rate

Table Columns:
- Checkbox
- Email
- Name
- Subscription Status (badge)
- Source
- Subscribed At
- Verified (checkmark)
- Last Email Sent
- Actions (view, unsubscribe, delete)

Filters:
- Subscription Status (Subscribed, Unsubscribed, Bounced, Complained)
- Source
- Verified/Unverified
- Date range

Features:
- Bulk unsubscribe
- Export subscribers list
- Import subscribers (CSV)
- Send test email
- View subscription history
- Resend verification email

Detail View:
- Subscriber information
- Subscription timeline
- Email preferences
- Engagement stats (opens, clicks)
- Unsubscribe reason (if applicable)

API Integration:
- GET /api/newsletter/subscribers/
- GET /api/newsletter/subscribers/:id/
- PATCH /api/newsletter/subscribers/:id/
- POST /api/newsletter/unsubscribe/

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- TanStack Table
- React Query
```

---

## Authentication & Verification

### 10. Email Verification Page

**Prompt:**
```
Create an email verification page for waitlist and newsletter:

Design:
- Centered card layout
- Success/error states
- Loading spinner during verification
- Clear messaging

Features:
- Token validation from URL query parameter
- Success state: "Email verified! You're on the waitlist."
- Error state: "Invalid or expired verification link"
- Resend verification email option
- Redirect to waitlist status page after success

API Integration:
- POST /api/waitlist/verify/ (body: { token })
- POST /api/newsletter/verify/ (body: { email, token })
- Handle 200 (success), 400 (invalid token), 404 (not found)

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components (Card, Button, Alert)
```

### 11. Waitlist Status Check Page

**Prompt:**
```
Create a waitlist status check page:

Design:
- Simple form with email input
- Status display card
- Clean, minimal design

Features:
- Email input with validation
- Submit button
- Status display:
  - Pending: "You're on the waitlist! We'll notify you soon."
  - Approved: "Congratulations! You've been approved."
  - Invited: "Check your email for your invitation."
  - Onboarded: "Welcome! You're all set."
  - Declined: "Unfortunately, your application was declined."

API Integration:
- GET /api/waitlist/status/:email/
- Display: status, priority_score, position (if available), created_at

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
```

---

## GDPR & Compliance

### 12. GDPR Consent Management Page

**Prompt:**
```
Create a GDPR consent management page:

Design:
- Clean, accessible design
- Clear consent options
- Privacy policy link
- Confirmation messages

Features:
- Consent types:
  - Marketing emails (checkbox)
  - Analytics tracking (checkbox)
  - Cookies (checkbox with categories)
- Privacy policy link (opens in modal or new tab)
- Save preferences button
- Success confirmation
- Withdraw consent option

API Integration:
- POST /api/gdpr/consent/ (body: { email, consent_type, consent_given })
- Handle multiple consent types

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components (Checkbox, Button, Alert, Dialog)
```

### 13. GDPR Data Export/Delete Page

**Prompt:**
```
Create a GDPR data management page:

Design:
- Tabbed interface: Export Data | Delete Data
- Clear warnings for delete action
- Confirmation dialogs

Export Tab:
- Email input
- "Export My Data" button
- Success: "Your data export will be emailed to you shortly"
- Download link (if immediate)

Delete Tab:
- Email input
- Warning message about data deletion
- Confirmation checkbox: "I understand this action cannot be undone"
- "Delete My Data" button (destructive style)
- Final confirmation dialog

API Integration:
- GET /api/gdpr/export/:email/
- GET /api/gdpr/access/:email/
- DELETE /api/gdpr/delete/:email/?confirmation=true

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components (Tabs, Input, Button, Alert, Dialog)
```

---

## Analytics & Reporting

### 14. Analytics Dashboard Page

**Prompt:**
```
Create an analytics dashboard page for admins:

Layout:
- Date range picker (last 7 days, 30 days, custom)
- KPI cards at top
- Charts grid below
- Data table at bottom

KPI Cards:
- Total Page Views
- Unique Visitors
- Total Events
- Conversion Rate
- Average Session Duration

Charts:
1. Page Views Over Time (Line chart, last 30 days)
2. Top Pages (Bar chart, top 10)
3. Event Categories (Pie chart)
4. Conversions Over Time (Area chart)
5. Traffic Sources (Donut chart)
6. User Flow (Sankey diagram, optional)

Data Tables:
- Recent Page Views (with filters)
- Recent Events (with filters)
- Recent Conversions (with filters)

Features:
- Real-time toggle
- Export data (CSV, PDF)
- Filter by date range, page, event type
- Drill-down on charts
- Custom date range picker

API Integration:
- GET /api/analytics/dashboard/?start_date=&end_date=
- GET /api/analytics/pageviews/
- GET /api/analytics/events/
- GET /api/analytics/conversions/

Tech Stack:
- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- Recharts for charts
- TanStack Table
- React Query
- date-fns
```

---

## Component Library

### 15. Reusable Form Components

**Prompt:**
```
Create a reusable form component library with:

Components:
1. FormInput - Text input with label, error, and validation
2. FormSelect - Dropdown with search, multi-select option
3. FormTextarea - Textarea with character count
4. FormCheckbox - Checkbox with label and description
5. FormRadio - Radio button group
6. FormDatePicker - Date picker with range option
7. FormFileUpload - File upload with preview
8. FormRating - Star rating input
9. FormSwitch - Toggle switch
10. FormSlider - Range slider

Features:
- Consistent styling
- Error states
- Loading states
- Disabled states
- Accessibility (ARIA labels)
- Validation messages
- Helper text
- Required indicators

Tech Stack:
- React + TypeScript
- Tailwind CSS
- Shadcn/ui base components
- React Hook Form integration
- Zod validation support
```

### 16. Data Table Component

**Prompt:**
```
Create a reusable data table component with:

Features:
- Sortable columns
- Filterable columns
- Search functionality
- Pagination
- Row selection (single/multiple)
- Column visibility toggle
- Export to CSV
- Responsive design
- Loading states
- Empty states
- Row actions menu

Props:
- data: array of objects
- columns: column definitions
- onRowClick: callback
- onSelectionChange: callback
- pagination: page, pageSize, total
- loading: boolean
- filters: filter configuration

Tech Stack:
- React + TypeScript
- Tailwind CSS
- TanStack Table
- Shadcn/ui components
```

### 17. Status Badge Component

**Prompt:**
```
Create a status badge component library:

Variants:
- Contact Status: new (blue), contacted (yellow), resolved (green), archived (gray)
- Waitlist Status: pending (yellow), approved (green), invited (blue), onboarded (green), declined (red)
- Lead Status: new (blue), contacted (yellow), qualified (green), unqualified (gray), converted (green), lost (red)
- Newsletter Status: subscribed (green), unsubscribed (gray), bounced (red), complained (orange)
- Priority: low (gray), medium (yellow), high (orange), urgent (red)

Features:
- Color-coded badges
- Icons (optional)
- Tooltip on hover
- Consistent sizing
- Accessible

Tech Stack:
- React + TypeScript
- Tailwind CSS
- Shadcn/ui Badge component
- Lucide React icons
```

---

## Design System Guidelines

### Color Palette
```
Primary: Blue (#3B82F6)
Secondary: Purple (#8B5CF6)
Success: Green (#10B981)
Warning: Yellow (#F59E0B)
Error: Red (#EF4444)
Neutral: Gray scale (#F9FAFB to #111827)
```

### Typography
```
Headings: Inter or Poppins
Body: Inter or System font
Sizes: text-xs (12px) to text-4xl (36px)
```

### Spacing
```
Tailwind default spacing scale
Consistent padding/margins
```

### Components Style
```
- Rounded corners (rounded-lg default)
- Subtle shadows
- Smooth transitions
- Hover states
- Focus states (accessibility)
```

---

## API Base Configuration

All components should use:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Example API call
const response = await fetch(`${API_BASE_URL}/api/waitlist/join/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
});
```

---

## Notes for v0.dev

1. **Always include error handling** - Show user-friendly error messages
2. **Loading states** - Use skeleton loaders or spinners
3. **Responsive design** - Mobile-first approach
4. **Accessibility** - ARIA labels, keyboard navigation
5. **TypeScript** - Use proper types for all props and API responses
6. **Form validation** - Client-side validation before API calls
7. **Rate limiting** - Handle 429 errors gracefully
8. **Success feedback** - Clear confirmation messages
9. **Empty states** - Friendly messages when no data
10. **Consistent styling** - Use Tailwind utility classes, Shadcn/ui components

---

## Quick Start Template

For any new page, use this structure:

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function PageName() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/endpoint/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error('Something went wrong');
      }
      
      // Handle success
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6">
      {/* Your component JSX */}
    </div>
  );
}
```

---

**Last Updated:** 2024-01-XX
**Version:** 1.0.0

