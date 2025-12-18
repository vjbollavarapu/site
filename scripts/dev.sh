#!/bin/bash

# Development script to run both backend and frontend
# Usage: ./scripts/dev.sh

set -e

echo "🚀 Starting Site Backend Monorepo Development Servers..."
echo ""

# Check if .env files exist
if [ ! -f "apps/backend/.env.local" ]; then
    echo "⚠️  Warning: apps/backend/.env.local not found"
    echo "   Copy apps/backend/.env.example to apps/backend/.env.local"
fi

if [ ! -f "apps/frontend/.env.local" ]; then
    echo "⚠️  Warning: apps/frontend/.env.local not found"
    echo "   Copy apps/frontend/.env.example to apps/frontend/.env.local"
fi

# Start backend
echo "📦 Starting Django backend..."
cd apps/backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Start backend server in background
echo "🌐 Starting backend server on http://localhost:8000..."
python manage.py runserver 8000 &
BACKEND_PID=$!

cd ../..

# Start frontend
echo "⚛️  Starting Next.js frontend..."
cd apps/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    pnpm install
fi

# Start frontend server
echo "🌐 Starting frontend server on http://localhost:3000..."
pnpm dev &
FRONTEND_PID=$!

cd ../..

echo ""
echo "✅ Development servers started!"
echo ""
echo "📊 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs/"
echo "⚛️  Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait

