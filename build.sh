#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Run migrations (automatically runs on every deploy)
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input

