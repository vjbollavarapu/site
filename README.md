# Site Backend Monorepo

A monorepo containing the Django REST API backend and Next.js frontend for the Site Backend project.

## 📁 Project Structure

```
sitebackend/
├── apps/
│   ├── backend/          # Django REST API
│   │   ├── apps/         # Django apps (contacts, waitlist, leads, etc.)
│   │   ├── sitebackend/  # Django project settings
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   └── ...
│   └── frontend/         # Next.js frontend
│       ├── app/          # Next.js app directory
│       ├── components/   # React components
│       ├── lib/          # Utilities and API client
│       ├── package.json
│       └── ...
├── docker-compose.yml    # Docker setup for both services
├── .env.example          # Environment variables template
├── package.json          # Root workspace configuration
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 8.0.0 (recommended) or npm
- **Python** >= 3.10.0
- **PostgreSQL** >= 12.0
- **Redis** (optional, for Celery)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sitebackend
   ```

2. **Install dependencies**
   ```bash
   # Install root dependencies
   npm install
   
   # Install frontend dependencies
   cd apps/frontend
   pnpm install
   cd ../..
   
   # Setup Python virtual environment for backend
   cd apps/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd ../..
   ```

3. **Configure environment variables**
   ```bash
   # Copy example files
   cp .env.example .env
   cp apps/backend/.env.example apps/backend/.env.local
   cp apps/frontend/.env.example apps/frontend/.env.local
   
   # Edit .env files with your configuration
   ```

4. **Setup database**
   ```bash
   # Run migrations
   npm run migrate
   ```

5. **Start development servers**
   ```bash
   # Start both backend and frontend
   npm run dev
   
   # Or start individually:
   npm run dev:backend    # Django on http://localhost:8000
   npm run dev:frontend   # Next.js on http://localhost:3000
   ```

## 🛠️ Available Scripts

### Root Level

- `npm run dev` - Start both backend and frontend in development mode
- `npm run build` - Build both projects for production
- `npm run test` - Run tests for both projects
- `npm run lint` - Lint both projects
- `npm run migrate` - Run Django migrations
- `npm run makemigrations` - Create Django migrations
- `npm run docker:up` - Start services with Docker Compose
- `npm run docker:down` - Stop Docker services

### Backend (Django)

```bash
cd apps/backend

# Development
python manage.py runserver          # Start dev server
python manage.py migrate            # Run migrations
python manage.py makemigrations     # Create migrations
python manage.py collectstatic      # Collect static files
python manage.py createsuperuser    # Create admin user

# Testing
python manage.py test               # Run all tests
python manage.py test apps.contacts # Test specific app

# Management commands
python manage.py shell              # Django shell
```

### Frontend (Next.js)

```bash
cd apps/frontend

# Development
pnpm dev          # Start dev server (http://localhost:3000)
pnpm build        # Build for production
pnpm start        # Start production server
pnpm lint         # Run ESLint
```

## 🐳 Docker Setup

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env.local)

See `apps/backend/.env.example` for all available variables. Key variables:

- `DEBUG=True` - Development mode
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection (optional)
- `EMAIL_HOST` - SMTP server
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

#### Frontend (.env.local)

- `NEXT_PUBLIC_API_URL=http://localhost:8000` - Backend API URL
- `NEXT_PUBLIC_APP_URL=http://localhost:3000` - Frontend URL

### CORS Configuration

The backend is configured to allow requests from the frontend. Update `CORS_ALLOWED_ORIGINS` in `apps/backend/sitebackend/settings.py` if needed.

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🏗️ Architecture

### Backend (Django)

- **Framework**: Django 5.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **API Documentation**: drf-spectacular (OpenAPI 3.0)

### Frontend (Next.js)

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn/ui
- **State Management**: React Query (SWR)
- **Forms**: React Hook Form + Zod

## 🔌 API Integration

The frontend connects to the backend API. Update the API base URL in:

- `apps/frontend/lib/api.ts` - API client configuration
- `apps/frontend/.env.local` - Environment variable `NEXT_PUBLIC_API_URL`

### Example API Call

```typescript
// apps/frontend/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchContacts() {
  const response = await fetch(`${API_BASE_URL}/api/contacts/`, {
    headers: {
      'Authorization': `Basic ${authToken}`,
    },
  });
  return response.json();
}
```

## 📦 Deployment

### Backend

1. Set `DEBUG=False` in production
2. Configure `ALLOWED_HOSTS`
3. Set up PostgreSQL database
4. Run migrations: `python manage.py migrate`
5. Collect static files: `python manage.py collectstatic`
6. Use Gunicorn or uWSGI as WSGI server

### Frontend

1. Build: `pnpm build`
2. Start: `pnpm start`
3. Or deploy to Vercel/Netlify

See `docs/DEPLOYMENT_CHECKLIST.md` for detailed deployment guide.

## 🧪 Testing

```bash
# Backend tests
cd apps/backend
python manage.py test

# Frontend tests
cd apps/frontend
pnpm test
```

## 📝 Development Guidelines

### Code Style

- **Backend**: Follow PEP 8, use Black for formatting
- **Frontend**: Follow ESLint rules, use Prettier for formatting

### Git Workflow

- Use feature branches
- Commit messages should be clear and descriptive
- Run tests before pushing

### Adding New Features

1. Create feature branch
2. Implement backend API endpoints
3. Update API documentation
4. Implement frontend components
5. Write tests
6. Update documentation
7. Create pull request

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🔗 Links

- **Backend API Docs**: http://localhost:8000/api/docs/
- **Frontend**: http://localhost:3000
- **Postman Collection**: `apps/backend/API_POSTMAN_COLLECTION.json`

## 🆘 Troubleshooting

### Backend Issues

- **Database connection errors**: Check PostgreSQL is running and `DATABASE_URL` is correct
- **Migration errors**: Run `python manage.py migrate --run-syncdb`
- **Static files not loading**: Run `python manage.py collectstatic`

### Frontend Issues

- **API connection errors**: Check `NEXT_PUBLIC_API_URL` and CORS settings
- **Build errors**: Clear `.next` folder and rebuild
- **Type errors**: Run `pnpm type-check` (if available)

### Common Solutions

- Clear caches: `rm -rf apps/frontend/.next apps/backend/__pycache__`
- Reinstall dependencies: `rm -rf node_modules apps/frontend/node_modules && npm install`
- Reset database: `python manage.py flush` (development only)

---

**Last Updated**: 2024-01-XX

