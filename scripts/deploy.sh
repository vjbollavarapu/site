#!/bin/bash

# Deployment script for Site Backend
# Usage: ./scripts/deploy.sh [environment]
# Example: ./scripts/deploy.sh production

set -e  # Exit on error

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env.$ENVIRONMENT" ]; then
    echo_error ".env.$ENVIRONMENT file not found!"
    exit 1
fi

echo_info "Starting deployment to $ENVIRONMENT..."

# Load environment variables
export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)

# Pre-deployment checks
echo_info "Running pre-deployment checks..."

# Check if tests pass
echo_info "Running tests..."
python manage.py test --keepdb || {
    echo_error "Tests failed! Aborting deployment."
    exit 1
}

# Check migrations
echo_info "Checking for pending migrations..."
python manage.py makemigrations --check --dry-run || {
    echo_warn "Pending migrations detected. Run 'python manage.py makemigrations' first."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

# Backup database (if updating existing)
if [ "$ENVIRONMENT" = "production" ]; then
    echo_info "Creating database backup..."
    ./scripts/backup.sh "$ENVIRONMENT" || {
        echo_warn "Backup failed, but continuing..."
    }
fi

# Docker deployment
if [ -f "docker-compose.yml" ]; then
    echo_info "Deploying with Docker..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
    else
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    # Build images
    echo_info "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build
    
    # Run migrations
    echo_info "Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" run --rm web python manage.py migrate
    
    # Collect static files
    echo_info "Collecting static files..."
    docker-compose -f "$COMPOSE_FILE" run --rm web python manage.py collectstatic --noinput
    
    # Start services
    echo_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for health checks
    echo_info "Waiting for services to be healthy..."
    sleep 10
    
    # Health check
    echo_info "Performing health check..."
    if curl -f http://localhost:8000/admin/login/ > /dev/null 2>&1; then
        echo_info "Health check passed!"
    else
        echo_error "Health check failed!"
        exit 1
    fi
    
else
    # Non-Docker deployment
    echo_info "Deploying without Docker..."
    
    # Activate virtual environment if exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Run migrations
    echo_info "Running database migrations..."
    python manage.py migrate
    
    # Collect static files
    echo_info "Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Restart services (adjust based on your setup)
    echo_info "Restarting services..."
    # Example: systemctl restart gunicorn
    # Example: supervisorctl restart sitebackend
fi

# Post-deployment verification
echo_info "Running post-deployment verification..."

# Check if application is responding
if curl -f http://localhost:8000/admin/login/ > /dev/null 2>&1; then
    echo_info "Application is responding!"
else
    echo_error "Application is not responding!"
    exit 1
fi

# Run smoke tests
echo_info "Running smoke tests..."
python manage.py check --deploy || {
    echo_warn "Django check warnings detected."
}

echo_info "Deployment to $ENVIRONMENT completed successfully!"
echo_info "Application URL: http://localhost:8000"
echo_info "Admin URL: http://localhost:8000/admin/"
echo_info "API Docs: http://localhost:8000/api/docs/"

