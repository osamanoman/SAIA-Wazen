#!/bin/bash

# SAIA Project Deployment Script
echo "Starting SAIA Project Deployment..."

# Navigate to project directory
cd /root/SAIA-noRAG-Wazen

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install PostgreSQL
echo "Installing PostgreSQL..."
apt update
apt install -y postgresql postgresql-contrib

# Start PostgreSQL service
echo "Starting PostgreSQL service..."
systemctl start postgresql
systemctl enable postgresql

# Create database and user
echo "Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE saia_db;"
sudo -u postgres psql -c "CREATE USER saia_user WITH PASSWORD 'saia_password_2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE saia_db TO saia_user;"
sudo -u postgres psql -c "ALTER USER saia_user CREATEDB;"

# Run migrations
echo "Running Django migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Set up permissions
echo "Setting up permissions..."
python manage.py setup_permissions --assign-all

echo "Deployment completed successfully!"
echo "You can now start the server with: python manage.py runserver 0.0.0.0:8000"
