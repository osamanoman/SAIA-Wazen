# SAIA Business Management System

A comprehensive Django-based business management system with dual AI assistants and multi-database architecture.

## 🚀 Features

### Core Business Management
- **Product Management**: Complete product lifecycle management with company-based filtering
- **Company & Branch Management**: Multi-company support with hierarchical organization
- **Invoice & Transaction Management**: Full invoicing system with detailed tracking
- **User Management**: Role-based access control with admin and customer user types

### AI Assistant Capabilities
- **Admin AI Assistant**: Full system management for staff users
- **Customer AI Assistant**: Read-only database queries for customer users
- **Natural Language Processing**: Query business data using natural language
- **Multi-language Support**: Arabic and English language support

### Multi-Database Architecture
- **System Database**: PostgreSQL for SAIA system data (users, permissions, etc.)
- **Customer Database**: MySQL for customer business data (invoices, products, etc.)
- **Smart Routing**: Automatic query routing to appropriate databases
- **Data Isolation**: Complete separation between admin and customer contexts

### Security & Monitoring
- **Context Separation**: Strict isolation between admin and customer data access
- **Read-Only Customer Access**: Customers can only query, never modify their data
- **Phoenix Observability**: Comprehensive AI assistant tracing and monitoring
- **Granular Permissions**: Fine-grained permission system for all operations

## 🏗️ Architecture

### Database Design
```
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      MySQL      │
│ (System Data)   │    │ (Customer Data) │
├─────────────────┤    ├─────────────────┤
│ • Users         │    │ • Invoices      │
│ • Permissions   │    │ • Contacts      │
│ • AI Threads    │    │ • Companies     │
│ • System Config │    │ • Transactions  │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 │
    ┌─────────────────────┐
    │  Database Router    │
    │  Smart Routing      │
    └─────────────────────┘
```

### AI Assistant Architecture
```
┌─────────────────┐    ┌─────────────────┐
│  Admin Users    │    │ Customer Users  │
│  (Staff)        │    │ (is_customer)   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ ProductAI       │    │ CustomerDataAI  │
│ Assistant       │    │ Assistant       │
│ • Full Access   │    │ • Read-Only     │
│ • System Data   │    │ • Customer Data │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- MySQL 8.0+
- Docker (optional, for MySQL)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd SAIA-noRAG-Wazen
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials and API keys
```

4. **Set up databases**
```bash
# PostgreSQL (System Database)
createdb saia_system

# MySQL (Customer Database) - Using Docker
docker run --name customer_mysql -e MYSQL_ROOT_PASSWORD=rootpass123 \
  -e MYSQL_DATABASE=customer_db -e MYSQL_USER=customer_user \
  -e MYSQL_PASSWORD=customer_pass123 -p 3306:3306 -d mysql:8.0
```

5. **Run migrations**
```bash
python manage.py migrate
python manage.py setup_permissions --assign-all
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start the development server**
```bash
python manage.py runserver
```

## 📖 Usage

### Admin Users
- Access full system functionality through Django admin
- Use ProductAI Assistant for system management
- Manage companies, users, and system configuration

### Customer Users
- Access customer-specific interface
- Use CustomerDataAI Assistant for data queries
- View and analyze their company's business data

### AI Assistant Queries
```
# Admin queries (ProductAI Assistant)
"Show me all products for company ABC"
"Create a new invoice for customer XYZ"
"What are the total sales this month?"

# Customer queries (CustomerDataAI Assistant)
"استخرج جميع الفواتير" (Extract all invoices)
"Show me my latest invoice"
"How many customers do we have?"
```

## 🔧 Configuration

### Database Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'saia_system',
        # ... PostgreSQL config
    },
    'client_data': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'customer_db',
        # ... MySQL config
    }
}
```

### AI Assistant Settings
```python
AI_ASSISTANT_CAN_RUN_ASSISTANT_FN = 'saia.permissions.ai_assistant_can_run_assistant'
AI_ASSISTANT_CAN_CREATE_THREAD_FN = 'saia.permissions.ai_assistant_can_create_thread'
AI_ASSISTANT_CAN_VIEW_THREAD_FN = 'saia.permissions.ai_assistant_can_view_thread'
```

## 🔒 Security

### Data Isolation
- Complete context separation between admin and customer users
- Customers can only access their own company's data
- Read-only access for customer database operations

### Permission System
- Granular permissions for all operations
- Role-based access control
- AI assistant permission validation

### Database Security
- Parameterized queries to prevent SQL injection
- Keyword filtering for dangerous operations
- Connection-level security with proper authentication

## 📊 Monitoring

### Phoenix Observability
- AI assistant tracing and monitoring
- Performance metrics and analytics
- Error tracking and debugging

Access Phoenix dashboard at: `http://localhost:6006`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the changelog for recent updates
