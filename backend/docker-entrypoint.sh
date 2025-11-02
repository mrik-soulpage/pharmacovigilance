#!/bin/bash
set -e

echo "=================================="
echo "Starting PharmaVigilance Backend"
echo "=================================="

# Wait for database to be ready (if using PostgreSQL)
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
fi

# Initialize database
echo "Initializing database..."
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"

# Import products from JSON
echo "Importing products from JSON..."
python init_products.py

# Start the application
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 600 run:app

