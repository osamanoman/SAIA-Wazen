# SAIA Django Project - Code Art Deployment Guide

## 🚀 Quick Start for Code Art CI/CD

This guide provides step-by-step instructions for deploying the SAIA Django project on Code Art (Huawei CodeArts) platform.

### ⚡ TL;DR - What You Need to Do

1. **Commit the new files** to your repository:
   - `setup.py` - Python package configuration
   - `MANIFEST.in` - File inclusion rules
   - `CODEART_DEPLOYMENT_GUIDE.md` - This guide

2. **Push to Code Art** and trigger the build

3. **The build should now succeed** with `python setup.py bdist_egg`

4. **Configure environment variables** in Code Art for production deployment

## 📋 Prerequisites

- Code Art account with CI/CD access
- Git repository uploaded to Code Art
- Basic understanding of Django and Docker

## 🔧 Installation Files Overview

The project now includes the following files specifically for Code Art deployment:

### 1. `setup.py` - Python Package Configuration
- **Purpose**: Satisfies Code Art's Python package build requirements
- **Function**: Handles `python setup.py bdist_egg` command that Code Art executes
- **Dependencies**: Automatically reads from `requirements.txt`

### 2. `MANIFEST.in` - Package File Inclusion
- **Purpose**: Specifies which files to include in the Python package
- **Includes**: Templates, static files, migrations, configuration files
- **Excludes**: Development files, logs, databases, build artifacts

### 3. `requirements.txt` - Python Dependencies
- **Purpose**: Lists all Python packages needed for the project
- **Count**: 121+ packages including Django, AI libraries, database drivers
- **Production Ready**: Includes Gunicorn, WhiteNoise for production deployment

## 🏗️ Code Art Build Configuration

### Build Process
When you trigger a build in Code Art, it will:

1. **Checkout Code**: Download your repository
2. **Python Setup**: Use Python 3.6+ environment (configurable)
3. **Package Build**: Run `python setup.py bdist_egg`
4. **Dependency Installation**: Install packages from `requirements.txt`
5. **Artifact Creation**: Generate deployable package

### Expected Build Output
```bash
running bdist_egg
running egg_info
creating saia_business_system.egg-info
...
creating 'dist/saia_business_system-1.0.0-py3.11.egg'
```

## 🐳 Docker Deployment (Recommended)

For production deployment, use the included Docker configuration:

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 2. Required Environment Variables
```bash
# Django Configuration
SECRET_KEY=your-super-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DB_NAME=saia_db
DB_USER=saia_user
DB_PASSWORD=your-secure-password
DB_HOST=your-db-host
DB_PORT=5432

# AI Configuration
GROQ_API_KEY=your-groq-api-key
```

### 3. Docker Deployment Commands
```bash
# Build and deploy everything
./deploy.sh deploy

# Or deploy with specific environment
./deploy.sh deploy .env.production

# Check status
./deploy.sh status

# View logs
./deploy.sh logs saia-wazen
```

## 🔍 Testing the Installation

### Local Testing
Before deploying to Code Art, test locally:

```bash
# Test setup.py
python setup.py --help-commands
python setup.py bdist_egg

# Test Django application
python manage.py check
python manage.py migrate
python manage.py runserver
```

### Docker Testing
```bash
# Build Docker image
docker build -t saia-wazen-test .

# Run with docker-compose
docker-compose up -d

# Check health
curl http://localhost:8000/health/
```

## ✅ Installation Success Verification

After creating the setup files, you can verify everything works locally:

```bash
# Test the setup.py file
python setup.py --help-commands
python setup.py check
python setup.py bdist_egg

# Verify the build artifacts
ls -la dist/
# Should show:
# saia-business-system-1.0.0.tar.gz
# saia_business_system-1.0.0-py3.11.egg
```

## 🚨 Common Issues and Solutions

### Issue 1: Python Version Mismatch
**Problem**: Code Art uses Python 3.6, but project requires 3.11+
**Solution**: Configure Code Art to use Python 3.11+ or adjust requirements

### Issue 2: Missing Dependencies
**Problem**: Some packages fail to install
**Solution**: Check `requirements.txt` and ensure all versions are compatible

### Issue 3: Static Files Not Found
**Problem**: CSS/JS files not loading
**Solution**: Run `python manage.py collectstatic` after deployment

### Issue 4: Database Connection Errors
**Problem**: Cannot connect to database
**Solution**: Verify database credentials in `.env` file

### Issue 5: setup.py bdist_egg Command Fails
**Problem**: Code Art build fails with setup.py errors
**Solution**: Ensure all three files are committed: `setup.py`, `MANIFEST.in`, `requirements.txt`

## 📊 Project Structure for Code Art

```
SAIA-Wazen/
├── setup.py                    # Python package configuration
├── MANIFEST.in                 # Package file inclusion rules
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Multi-service setup
├── deploy.sh                   # Deployment automation
├── .env.example               # Environment template
├── saia/                      # Main Django project
├── widget/                    # Chatbot widget app
├── product/                   # Product management app
├── company/                   # Company management app
├── users/                     # User management app
├── invoice/                   # Invoice management app
├── project/                   # Project management app
├── static/                    # Static files
├── templates/                 # Django templates
├── media/                     # Media files
└── logs/                      # Application logs
```

## 🎯 Next Steps

1. **Upload to Code Art**: Ensure all files are committed to your repository
2. **Configure Build**: Set up CI/CD pipeline in Code Art interface
3. **Environment Variables**: Configure production environment variables
4. **Database Setup**: Prepare PostgreSQL and MySQL databases
5. **Domain Configuration**: Set up domain and SSL certificates
6. **Monitoring**: Configure logging and monitoring

## 📞 Support

If you encounter issues during deployment:

1. Check the build logs in Code Art interface
2. Verify all environment variables are set correctly
3. Test the setup.py file locally first
4. Ensure Docker configuration is working locally

## 🔐 Security Considerations

- Never commit `.env` files with real credentials
- Use strong passwords for database connections
- Configure proper firewall rules
- Enable SSL/HTTPS in production
- Regularly update dependencies

---

**Note**: This guide assumes you're using Huawei CodeArts platform. Adjust configurations as needed for your specific deployment environment.
