#!/bin/bash

# Database migration script
# Usage: ./scripts/migrate.sh [environment]
# Example: ./scripts/migrate.sh production

set -e  # Exit on error

ENVIRONMENT=${1:-development}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

echo_info "Running database migrations for $ENVIRONMENT..."

# Check if .env file exists
if [ -f ".env.$ENVIRONMENT" ]; then
    export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)
fi

# Docker deployment
if [ -f "docker-compose.yml" ]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
    else
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    echo_info "Running migrations in Docker container..."
    docker-compose -f "$COMPOSE_FILE" run --rm web python manage.py migrate
    
else
    # Non-Docker deployment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    echo_info "Running migrations..."
    python manage.py migrate
fi

# Show migration status
echo_info "Migration status:"
if [ -f "docker-compose.yml" ]; then
    docker-compose -f "$COMPOSE_FILE" run --rm web python manage.py showmigrations
else
    python manage.py showmigrations
fi

echo_info "Migrations completed successfully!"

