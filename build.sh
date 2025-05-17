#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies required for translations
apt-get update && apt-get install -y gettext

# Install Python dependencies
pip install -r requirements.txt

# Compile translation messages
python manage.py compilemessages || echo "Warning: compilemessages failed, continuing anyway"

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate 