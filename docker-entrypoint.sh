#!/bin/bash
set -e

echo "🚀 Starting khampha.online..."
echo "================================"

# Run database migrations
echo ""
echo "🔄 Running database migrations..."
python backend/database/run_migrations.py

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed"
else
    echo "⚠️  Database migrations had some issues, but continuing..."
fi

echo ""
echo "================================"
echo "🌐 Starting Flask application..."
echo ""

# Start the Flask application
exec python backend/app.py
