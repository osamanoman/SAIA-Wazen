# SAIA Project Deployment Guide

## Server Setup Commands

### 1. Connect to Server
```bash
ssh root@143.110.131.238
```

### 2. Navigate to Project Directory
```bash
cd /root/SAIA-noRAG-Wazen
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Install PostgreSQL
```bash
apt update
apt install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql
```

### 6. Set up Database
```bash
sudo -u postgres psql -c "CREATE DATABASE saia_db;"
sudo -u postgres psql -c "CREATE USER saia_user WITH PASSWORD 'saia_password_2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE saia_db TO saia_user;"
sudo -u postgres psql -c "ALTER USER saia_user CREATEDB;"
```

### 7. Run Migrations
```bash
python manage.py migrate
```

### 8. Create Superuser
```bash
python manage.py createsuperuser
```

### 9. Set up Permissions
```bash
python manage.py setup_permissions --assign-all
```

### 10. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 11. Start Server
```bash
python manage.py runserver 0.0.0.0:8000
```

## Environment Variables
Make sure the .env file is properly configured with:
- Database credentials
- Secret key
- Debug settings
- All required environment variables

## Access the Application
- URL: http://143.110.131.238:8000
- Admin: http://143.110.131.238:8000/admin
- Chat: http://143.110.131.238:8000/chat/
