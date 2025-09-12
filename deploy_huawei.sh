#!/bin/bash

# SAIA Wazen Deployment Script for Huawei Cloud
# This script deploys the SAIA Django application to Huawei Cloud ECS

echo "🚀 Starting SAIA Wazen Deployment to Huawei Cloud..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/saia-wazen
sudo chown $USER:$USER /opt/saia-wazen
cd /opt/saia-wazen

# Clone repository (replace with your Huawei Cloud repo URL)
echo "📥 Cloning repository..."
git clone https://codehub-cn-north-4.devcloud.huaweicloud.com/wazen-individual/saia-wazen.git .

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=your-domain.com,your-server-ip
DATABASE_URL=postgresql://saia_user:your_password@localhost/saia_db
REDIS_URL=redis://localhost:6379/0
PHOENIX_API_KEY=your-phoenix-api-key
EOF

# Setup PostgreSQL database
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE DATABASE saia_db;
CREATE USER saia_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE saia_db TO saia_user;
ALTER USER saia_user CREATEDB;
\q
EOF

# Run Django migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Create superuser (optional)
echo "👤 Creating Django superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@wazen.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Setup Nginx configuration
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/saia-wazen << EOF
server {
    listen 80;
    server_name your-domain.com your-server-ip;

    location /static/ {
        alias /opt/saia-wazen/static/;
    }

    location /media/ {
        alias /opt/saia-wazen/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/saia-wazen /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Create systemd service for Django
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/saia-wazen.service << EOF
[Unit]
Description=SAIA Wazen Django Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/saia-wazen
Environment=PATH=/opt/saia-wazen/venv/bin
ExecStart=/opt/saia-wazen/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable saia-wazen
sudo systemctl start saia-wazen
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Check service status
echo "✅ Checking service status..."
sudo systemctl status saia-wazen --no-pager
sudo systemctl status nginx --no-pager

echo "🎉 Deployment completed!"
echo "📝 Next steps:"
echo "1. Update .env file with your actual configuration"
echo "2. Configure your domain DNS to point to this server"
echo "3. Setup SSL certificate (Let's Encrypt recommended)"
echo "4. Test the application at http://your-server-ip"
echo ""
echo "🔗 Widget integration URL: http://your-domain.com/api/widget/"
echo "📊 Admin panel: http://your-domain.com/admin/"
echo ""
echo "🔧 Useful commands:"
echo "  - Check logs: sudo journalctl -u saia-wazen -f"
echo "  - Restart app: sudo systemctl restart saia-wazen"
echo "  - Update code: cd /opt/saia-wazen && git pull && sudo systemctl restart saia-wazen"
