# 🚀 SAIA Wazen Chatbot - Complete Production Deployment Guide

## 📋 **DEPLOYMENT OVERVIEW**

This guide provides step-by-step instructions for deploying the SAIA Multi-Tenant Chatbot Platform to your Huawei Cloud server using Docker containers.

### **Architecture Components**
- **Django Application**: SAIA Wazen Chatbot (Port 8000)
- **PostgreSQL**: Main SAIA database (Port 5432)
- **MySQL**: Client/Wazen data (Port 3307)
- **Redis**: Caching and sessions (Port 6379)
- **Phoenix**: AI monitoring and observability (Port 6006)

---

## 🔐 **STEP 1: SERVER ACCESS & PREPARATION**

### **1.1 Connect to Your Huawei Server**

```bash
# SSH into your Huawei Cloud server
ssh username@your-server-ip

# Or use Huawei Cloud Console if SSH is not available
```

### **1.2 Install Required Dependencies**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version
```

### **1.3 Clone Repository**

```bash
# Navigate to your deployment directory
cd /opt

# Clone your repository (if not already done)
git clone https://github.com/your-username/SAIA-Wazen.git
cd SAIA-Wazen

# Or pull latest changes if already cloned
git pull origin main
```

---

## ⚙️ **STEP 2: ENVIRONMENT CONFIGURATION**

### **2.1 Create Production Environment File**

```bash
# Copy the production template
cp .env.production .env

# Edit the environment file with your actual values
nano .env
```

### **2.2 Update Critical Configuration Values**

**🔑 REQUIRED CHANGES in .env:**

```bash
# Django Security
SECRET_KEY=your-actual-super-secret-key-minimum-50-characters-long
ALLOWED_HOSTS=your-server-ip,your-domain.com,localhost

# Database Passwords (CHANGE THESE!)
DB_PASSWORD=your_secure_postgresql_password_2024
CLIENT_DB_PASSWORD=your_secure_mysql_password_2024

# AI API Keys
GROQ_API_KEY=your-actual-groq-api-key
TOGETHER_API_KEY=your-actual-together-ai-key

# WhatsApp Business API (if using)
WHATSAPP_ACCESS_TOKEN=your-actual-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-actual-phone-id

# Widget Security
WIDGET_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Email Configuration (optional)
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=your-actual-app-password
```

### **2.3 Set Proper File Permissions**

```bash
# Secure the environment file
chmod 600 .env

# Create required directories
mkdir -p logs media staticfiles backups
chmod 755 logs media staticfiles backups
```

---

## 🐳 **STEP 3: DOCKER DEPLOYMENT**

### **3.1 Build and Deploy Using the Deployment Script**

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy with production environment
./deploy.sh deploy .env

# Or deploy step by step:
./deploy.sh build                    # Build Docker image
./deploy.sh start .env              # Start services
```

### **3.2 Manual Deployment (Alternative)**

```bash
# Build the Docker image
docker build -t saia-wazen-chatbot:latest .

# Start infrastructure services first
docker-compose up -d postgres mysql redis phoenix

# Wait for databases to be ready
sleep 30

# Check service health
docker-compose ps

# Start the main application
docker-compose up -d saia-wazen

# View logs
docker-compose logs -f saia-wazen
```

---

## 🗄️ **STEP 4: DATABASE SETUP**

### **4.1 Run Database Migrations**

```bash
# Run Django migrations
docker-compose exec saia-wazen python manage.py migrate --settings=saia.settings_production

# Create superuser account
docker-compose exec saia-wazen python manage.py createsuperuser --settings=saia.settings_production

# Load initial data (if available)
docker-compose exec saia-wazen python manage.py loaddata initial_data.json --settings=saia.settings_production
```

### **4.2 Verify Database Connections**

```bash
# Test PostgreSQL connection
docker-compose exec postgres psql -U saia_user -d saia_db -c "SELECT version();"

# Test MySQL connection
docker-compose exec mysql mysql -u wazen_user -p wazen_client_db -e "SELECT VERSION();"

# Test Redis connection
docker-compose exec redis redis-cli ping
```

---

## 🔍 **STEP 5: VERIFICATION & TESTING**

### **5.1 Health Checks**

```bash
# Check all service status
docker-compose ps

# Test application health endpoint
curl http://localhost:8000/health/

# Test widget demo page
curl http://localhost:8000/api/widget/demo/wazen/

# Check Phoenix monitoring
curl http://localhost:6006/
```

### **5.2 API Testing**

```bash
# Test widget configuration API
curl -X GET "http://localhost:8000/api/widget/config/wazen/" \
  -H "Content-Type: application/json"

# Test session creation
curl -X POST "http://localhost:8000/api/widget/session/create/wazen/" \
  -H "Content-Type: application/json" \
  -d '{"visitor_ip": "192.168.1.1"}'
```

---

## 🌐 **STEP 6: NGINX REVERSE PROXY (RECOMMENDED)**

### **6.1 Install and Configure Nginx**

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/saia-wazen
```

### **6.2 Nginx Configuration**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Main application
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /opt/SAIA-Wazen/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/SAIA-Wazen/media/;
        expires 1y;
    }

    # Phoenix monitoring (optional, secure this)
    location /monitoring/ {
        proxy_pass http://localhost:6006/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **6.3 Enable Nginx Configuration**

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/saia-wazen /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🔒 **STEP 7: SSL CERTIFICATE (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

---

## 📊 **STEP 8: MONITORING & LOGGING**

### **8.1 Set Up Log Rotation**

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/saia-wazen
```

```bash
/opt/SAIA-Wazen/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/SAIA-Wazen/docker-compose.yml restart saia-wazen
    endscript
}
```

### **8.2 System Monitoring**

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor Docker containers
docker stats

# Monitor logs in real-time
docker-compose logs -f --tail=100
```

---

## 💾 **STEP 9: BACKUP STRATEGY**

### **9.1 Database Backup Script**

```bash
# Create backup script
nano /opt/SAIA-Wazen/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/SAIA-Wazen/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
docker-compose exec -T postgres pg_dump -U saia_user saia_db > "$BACKUP_DIR/postgres_$DATE.sql"

# MySQL backup
docker-compose exec -T mysql mysqldump -u wazen_user -p wazen_client_db > "$BACKUP_DIR/mysql_$DATE.sql"

# Compress backups
gzip "$BACKUP_DIR/postgres_$DATE.sql"
gzip "$BACKUP_DIR/mysql_$DATE.sql"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

### **9.2 Schedule Automated Backups**

```bash
# Make backup script executable
chmod +x /opt/SAIA-Wazen/backup.sh

# Add to crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /opt/SAIA-Wazen/backup.sh
```

---

## 🚨 **STEP 10: TROUBLESHOOTING**

### **10.1 Common Issues**

```bash
# Check service status
./deploy.sh status

# View application logs
docker-compose logs saia-wazen

# Check database connectivity
docker-compose exec saia-wazen python manage.py check --settings=saia.settings_production

# Restart services
docker-compose restart

# Clean restart
docker-compose down && docker-compose up -d
```

### **10.2 Performance Optimization**

```bash
# Monitor resource usage
docker stats

# Optimize database
docker-compose exec postgres psql -U saia_user -d saia_db -c "VACUUM ANALYZE;"

# Clear Redis cache if needed
docker-compose exec redis redis-cli FLUSHALL
```

---

## ✅ **DEPLOYMENT CHECKLIST**

- [ ] Server dependencies installed (Docker, Docker Compose)
- [ ] Repository cloned and updated
- [ ] Environment file configured with production values
- [ ] Docker containers built and running
- [ ] Database migrations completed
- [ ] Superuser account created
- [ ] Health checks passing
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Monitoring and logging set up
- [ ] Backup strategy implemented
- [ ] Security headers configured
- [ ] API endpoints tested

---

## 🎉 **SUCCESS!**

Your SAIA Wazen Chatbot is now deployed and running in production!

**Access URLs:**
- **Main Application**: https://your-domain.com
- **Admin Panel**: https://your-domain.com/admin/
- **API Documentation**: https://your-domain.com/api/docs/
- **Widget Demo**: https://your-domain.com/api/widget/demo/wazen/
- **Phoenix Monitoring**: https://your-domain.com/monitoring/

**Next Steps:**
1. Configure your domain DNS to point to your server
2. Test all functionality thoroughly
3. Set up monitoring alerts
4. Configure automated backups
5. Document your deployment for your team

**Support:** If you encounter issues, check the logs and troubleshooting section above.
