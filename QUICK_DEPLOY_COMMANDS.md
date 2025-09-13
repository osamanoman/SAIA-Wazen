# ⚡ SAIA Wazen - Quick Deployment Commands

## 🚀 **IMMEDIATE DEPLOYMENT STEPS**

### **1. Server Preparation (Run on your Huawei server)**

```bash
# Update system
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
```

### **2. Repository Setup**

```bash
# Navigate to deployment directory
cd /opt

# Clone repository (if not done)
git clone https://github.com/your-username/SAIA-Wazen.git
cd SAIA-Wazen

# Or pull latest changes
git pull origin main
```

### **3. Environment Configuration**

```bash
# Copy production environment template
cp .env.production .env

# Edit with your actual values
nano .env
```

**🔑 CRITICAL VALUES TO UPDATE in .env:**

```bash
# Change these immediately:
SECRET_KEY=your-actual-50-character-secret-key-here
DB_PASSWORD=your_secure_postgresql_password
CLIENT_DB_PASSWORD=your_secure_mysql_password
ALLOWED_HOSTS=your-server-ip,your-domain.com,localhost

# Add your API keys:
GROQ_API_KEY=your-groq-api-key
TOGETHER_API_KEY=your-together-ai-key
```

### **4. Deploy with One Command**

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy everything
./deploy.sh deploy .env
```

### **5. Verify Deployment**

```bash
# Check service status
docker-compose ps

# Test application
curl http://localhost:8000/health/

# Test widget demo
curl http://localhost:8000/api/widget/demo/wazen/

# View logs
docker-compose logs -f saia-wazen
```

---

## 🔧 **MANUAL DEPLOYMENT (Alternative)**

If the deployment script fails, run these commands manually:

```bash
# 1. Build Docker image
docker build -t saia-wazen-chatbot:latest .

# 2. Start infrastructure services
docker-compose up -d postgres mysql redis phoenix

# 3. Wait for services to be ready
sleep 30

# 4. Check service health
docker-compose ps

# 5. Start main application
docker-compose up -d saia-wazen

# 6. Run database migrations
docker-compose exec saia-wazen python manage.py migrate --settings=saia.settings_production

# 7. Create superuser
docker-compose exec saia-wazen python manage.py createsuperuser --settings=saia.settings_production

# 8. Collect static files
docker-compose exec saia-wazen python manage.py collectstatic --noinput --settings=saia.settings_production
```

---

## 🌐 **NGINX SETUP (Recommended for Production)**

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/saia-wazen
```

**Nginx Configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com your-server-ip;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/SAIA-Wazen/staticfiles/;
    }

    location /media/ {
        alias /opt/SAIA-Wazen/media/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/saia-wazen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 **SSL Certificate (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## 📊 **MONITORING COMMANDS**

```bash
# Check all services
./deploy.sh status

# View real-time logs
docker-compose logs -f

# Monitor resource usage
docker stats

# Check application health
curl http://localhost:8000/health/

# Test API endpoints
curl -X GET "http://localhost:8000/api/widget/config/wazen/"
```

---

## 🚨 **TROUBLESHOOTING COMMANDS**

```bash
# Restart all services
docker-compose restart

# Clean restart
docker-compose down
docker-compose up -d

# View specific service logs
docker-compose logs saia-wazen
docker-compose logs postgres
docker-compose logs mysql
docker-compose logs redis

# Check database connectivity
docker-compose exec saia-wazen python manage.py check --settings=saia.settings_production

# Access container shell
docker-compose exec saia-wazen bash

# Check disk space
df -h

# Check memory usage
free -h
```

---

## 💾 **BACKUP COMMANDS**

```bash
# Create backup directory
mkdir -p backups

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U saia_user saia_db > backups/postgres_$(date +%Y%m%d).sql

# Backup MySQL
docker-compose exec -T mysql mysqldump -u wazen_user -p wazen_client_db > backups/mysql_$(date +%Y%m%d).sql

# Backup application files
tar -czf backups/app_$(date +%Y%m%d).tar.gz --exclude=backups --exclude=logs .
```

---

## ✅ **QUICK VERIFICATION CHECKLIST**

After deployment, verify these URLs work:

- [ ] `http://your-server-ip:8000/` - Main application
- [ ] `http://your-server-ip:8000/admin/` - Django admin
- [ ] `http://your-server-ip:8000/api/widget/demo/wazen/` - Widget demo
- [ ] `http://your-server-ip:8000/health/` - Health check
- [ ] `http://your-server-ip:6006/` - Phoenix monitoring

---

## 🎯 **NEXT STEPS AFTER DEPLOYMENT**

1. **Configure DNS**: Point your domain to your server IP
2. **Set up SSL**: Use Let's Encrypt for HTTPS
3. **Configure monitoring**: Set up alerts and logging
4. **Test thoroughly**: Verify all functionality works
5. **Set up backups**: Implement automated backup strategy
6. **Security review**: Ensure all security settings are correct

---

## 📞 **SUPPORT**

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables: `cat .env`
3. Check service status: `docker-compose ps`
4. Review the full deployment guide: `PRODUCTION_DEPLOYMENT_GUIDE.md`

**Your SAIA Wazen Chatbot should now be running successfully!** 🎉
