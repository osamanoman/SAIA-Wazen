# SAIA Project Structure

This document outlines the complete directory structure and organization of the SAIA Business Management System.

## 📁 Root Directory Structure

```
SAIA-Wazen/
├── 📄 manage.py                    # Django management script
├── 📄 requirements.txt             # Python dependencies
├── 📄 docker-compose.yml           # Docker configuration
├── 📄 deploy.sh                    # Deployment script
├── 📄 db.sqlite3                   # SQLite database (development)
├── 📄 .gitignore                   # Git ignore rules
├── 📄 README.md                    # Main project documentation
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 📂 saia/                        # Main Django project directory
├── 📂 company/                     # Company management app
├── 📂 users/                       # User management app
├── 📂 product/                     # Product & knowledge management app
├── 📂 invoice/                     # Invoice management app
├── 📂 project/                     # Project management app
│
├── 📂 static/                      # Static files (CSS, JS, images)
├── 📂 templates/                   # Django templates
├── 📂 media/                       # User uploaded files
├── 📂 logs/                        # Application logs
│
├── 📂 docs/                        # Documentation
├── 📂 scripts/                     # Utility scripts
├── 📂 data/                        # Data files and samples
├── 📂 config/                      # Configuration files
├── 📂 tests/                       # Test files
│
└── 📂 venv/                        # Virtual environment (excluded from git)
```

## 🏗️ Django Apps Structure

### 📂 saia/ (Main Project)
```
saia/
├── __init__.py
├── settings.py                     # Django settings
├── urls.py                         # URL routing
├── wsgi.py                         # WSGI configuration
├── asgi.py                         # ASGI configuration
├── database_router.py              # Multi-database routing
├── permissions.py                  # Custom permissions
├── knowledge_service.py            # Knowledge base service
├── client_data_service.py          # Client data service
├── base_ai_assistant.py            # Base AI assistant class
├── mixins.py                       # Utility mixins
├── middleware.py                   # Custom middleware
├── context_processors.py           # Template context processors
├── utils.py                        # Utility functions
└── management/                     # Management commands
```

### 📂 company/ (Company Management)
```
company/
├── __init__.py
├── models.py                       # Company and Branch models
├── admin.py                        # Django admin configuration
├── views.py                        # Views
├── apps.py                         # App configuration
├── signals.py                      # Django signals
├── tests.py                        # Unit tests
├── migrations/                     # Database migrations
└── management/                     # Management commands
```

### 📂 users/ (User Management)
```
users/
├── __init__.py
├── models.py                       # Custom User model
├── admin.py                        # User admin configuration
├── views.py                        # User views
├── apps.py                         # App configuration
├── tests.py                        # User tests
├── migrations/                     # Database migrations
└── management/                     # User management commands
```

### 📂 product/ (Product & Knowledge Management)
```
product/
├── __init__.py
├── models.py                       # Product, Knowledge models
├── admin.py                        # Product admin
├── views.py                        # Product views
├── ai_assistants.py                # AI assistant implementations
├── ai_tools_registry.py            # AI tools registry
├── apps.py                         # App configuration
├── tests.py                        # Product tests
├── assistants/                     # AI assistant modules
├── migrations/                     # Database migrations
└── management/                     # Product management commands
```

### 📂 invoice/ (Invoice Management)
```
invoice/
├── __init__.py
├── models.py                       # Invoice models
├── admin.py                        # Invoice admin
├── views.py                        # Invoice views
├── apps.py                         # App configuration
├── tests.py                        # Invoice tests
└── migrations/                     # Database migrations
```

### 📂 project/ (Project Management)
```
project/
├── __init__.py
├── models.py                       # Project models
├── admin.py                        # Project admin
├── views.py                        # Project views
├── urls.py                         # Project URLs
├── apps.py                         # App configuration
├── tests.py                        # Project tests
├── templates/                      # Project-specific templates
├── templatetags/                   # Custom template tags
└── migrations/                     # Database migrations
```

## 📚 Supporting Directories

### 📂 docs/ (Documentation)
```
docs/
├── README.md                       # Documentation index
├── CHANGELOG.md                    # Project changelog
├── readme.txt                     # Legacy readme
├── api/                           # API documentation
│   └── API.md
├── architecture/                  # Architecture docs
│   ├── MULTI_TENANT_AI_PRD.md
│   ├── FULL_STACK_REVIEW_COMPLETE.md
│   ├── CODEBASE_CLEANUP_SUMMARY.md
│   └── EXTRACTED_COMPONENTS_SUMMARY.md
├── deployment/                    # Deployment guides
│   ├── DEPLOYMENT_SUMMARY_v2.1.0.md
│   ├── CUSTOMER_DATABASE_SETUP.md
│   └── deployment_guide.md
├── features/                      # Feature documentation
│   ├── COMPANY_SPECIFIC_AI_ASSISTANTS.md
│   ├── TABLE_RENDERING_ENHANCEMENT.md
│   ├── WAZEN_INTEGRATION_COMPLETE.md
│   ├── PERMISSION_FIX_COMPANY_ASSISTANTS.md
│   ├── WAZEN_IMPLEMENTATION_PLAN.md
│   └── WAZEN_MISSING_CONTENT_RECOMMENDATIONS.md
└── guides/                        # User guides
    └── CUSTOMER_ONBOARDING_GUIDE.md
```

### 📂 scripts/ (Utility Scripts)
```
scripts/
├── README.md                       # Scripts documentation
├── data_management/               # Data management scripts
│   ├── add_knowledge_content.py
│   ├── add_knowledge_example.py
│   ├── add_wazen_content.py
│   ├── import_from_csv.py
│   └── import_wazen_faqs.py
├── setup/                         # Setup scripts
│   ├── setup_wazen_customer.py
│   └── cleanup_codebase.py
└── testing/                       # Testing scripts
    └── test_improvements.py
```

### 📂 data/ (Data Files)
```
data/
├── README.md                       # Data directory documentation
├── samples/                       # Sample data files
│   └── sample_knowledge_content.txt
├── wazen/                         # Wazen-specific data
│   ├── wazen content.docx
│   ├── wazen-data.md
│   └── FAQ.docx
└── sql/                           # SQL scripts
    └── init-db.sql
```

### 📂 tests/ (Test Files)
```
tests/
├── html/                          # HTML test files
│   └── test_intelligent_responses.html
├── test_phase2_company_ai_config.py
├── test_phase3_dynamic_ai_config.py
├── test_phase4_tool_registry.py
├── test_phase5_enhanced_routing.py
└── test_phase6_end_to_end.py
```

### 📂 static/ (Static Files)
```
static/
├── admin/                         # Django admin static files
├── assets/                        # Project assets
├── css/                           # Stylesheets
├── fonts/                         # Font files
└── js/                            # JavaScript files
```

### 📂 templates/ (Django Templates)
```
templates/
├── admin/                         # Admin template overrides
└── home.html                      # Home page template
```

### 📂 media/ (User Uploads)
```
media/
└── uploads/                       # User uploaded files
```

### 📂 config/ (Configuration)
```
config/
└── environments/                  # Environment-specific configs
```

### 📂 logs/ (Application Logs)
```
logs/                              # Application log files
```

## 🔧 Key Files

### Configuration Files
- **saia/settings.py** - Main Django settings
- **docker-compose.yml** - Docker configuration
- **requirements.txt** - Python dependencies
- **.gitignore** - Git ignore rules

### Entry Points
- **manage.py** - Django management commands
- **saia/wsgi.py** - WSGI application
- **saia/asgi.py** - ASGI application

### Database
- **saia/database_router.py** - Multi-database routing
- ***/migrations/** - Database migration files

### AI Assistants
- **product/ai_assistants.py** - Main AI assistant implementations
- **saia/base_ai_assistant.py** - Base AI assistant class
- **saia/knowledge_service.py** - Knowledge retrieval service

## 📋 Maintenance Guidelines

### File Organization
1. **Keep related files together** in appropriate app directories
2. **Use descriptive names** for files and directories
3. **Maintain consistent structure** across similar components
4. **Document new directories** in this file

### Code Organization
1. **Follow Django conventions** for app structure
2. **Separate concerns** appropriately (models, views, services)
3. **Use mixins and base classes** for shared functionality
4. **Keep configuration centralized** in settings

### Documentation
1. **Update this file** when structure changes
2. **Maintain README files** in each major directory
3. **Document purpose** of new directories or files
4. **Keep documentation current** with code changes
