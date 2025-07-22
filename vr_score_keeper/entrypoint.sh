#!/bin/sh

# This script is a simple entrypoint for the Django application.
# It ensures that database migrations and static file collection
# are handled before the main application server starts.

# Exit immediately if a command exits with a non-zero status.
set -e

# It's good practice to wait for the database to be ready, especially in production.
# For a more robust solution, you could use a tool like wait-for-it.sh and install netcat.
# For now, a simple sleep can prevent some race conditions on initial setup.
# echo "Waiting for database..."
# sleep 5

# Apply database migrations.
echo "Applying database migrations..."
python manage.py migrate --no-input

# Collect static files. This is crucial for whitenoise to serve your static assets.
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# The CMD from the Dockerfile will be passed as arguments to this script.
exec "$@"