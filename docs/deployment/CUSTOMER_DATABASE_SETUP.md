# Customer Database Setup Guide

## Overview
Each customer can have their own dedicated database for AI queries while sharing the same SAIA system database for user management and AI conversations.

## Database Configuration

### 1. Company Database Configuration (database_config_json)

```json
{
    "host": "customer-db-server.com",
    "name": "customer_business_db", 
    "user": "customer_readonly",
    "password": "secure_password",
    "port": 3306,
    "charset": "utf8mb4"
}
```

**Required Fields:**
- `host`: Database server hostname/IP
- `name`: Database name
- `user`: Database username (should be read-only)

**Optional Fields:**
- `password`: Database password (default: empty)
- `port`: Database port (default: 3306)
- `charset`: Character set (default: utf8mb4)

### 2. AI Tools Configuration (enabled_tools_json)

```json
[
    "get_all_invoices",
    "get_invoice_count", 
    "get_contacts",
    "get_database_overview",
    "search_customer_data",
    "list_customer_tables",
    "get_customer_table_sample",
    "describe_customer_table",
    "count_customer_table_rows",
    "get_comprehensive_database_overview",
    "test_customer_database_connection",
    "get_invoice_by_number",
    "get_latest_invoice"
]
```

## Setup Process

### Step 1: Create Customer Database
```sql
CREATE DATABASE customer_company_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'company_readonly'@'%' IDENTIFIED BY 'secure_password';
GRANT SELECT ON customer_company_db.* TO 'company_readonly'@'%';
FLUSH PRIVILEGES;
```

### Step 2: Configure Company in Django Admin
1. Go to Django Admin → Companies
2. Edit the customer's company
3. Set `database_config_json` with connection details
4. Set `enabled_tools_json` with desired AI tools
5. Save the company

### Step 3: Test Connection
```python
from users.models import User
from saia.client_data_service import ClientDataService

user = User.objects.get(username='customer_user')
service = ClientDataService(user=user)

# Test connection
result = service.execute_safe_query("SELECT 1 as test")
print(result)  # Should return [{'test': 1}]
```

## Security Features

### Database Security
- **Read-Only Access**: Customer databases use read-only MySQL users
- **Query Restrictions**: Only SELECT, SHOW, DESCRIBE queries allowed
- **Connection Isolation**: Each company connects to their own database
- **Parameterized Queries**: All queries use parameter binding

### Data Isolation
- **Company-Based Routing**: Users automatically connect to their company database
- **No Cross-Company Access**: Users cannot access other companies' data
- **Admin Oversight**: SAIA admins can manage all companies but customers see only their own data

## Business Types & Tool Configurations

### General Business
```json
["get_all_invoices", "get_contacts", "get_database_overview", "search_customer_data"]
```

### E-commerce
```json
["get_all_invoices", "get_contacts", "search_customer_data", "count_customer_table_rows"]
```

### Insurance
```json
["get_all_invoices", "get_contacts", "get_comprehensive_database_overview", "test_customer_database_connection"]
```

### Manufacturing
```json
["get_database_overview", "list_customer_tables", "describe_customer_table", "get_customer_table_sample"]
```

## Troubleshooting

### Connection Issues
1. Check database credentials in `database_config_json`
2. Verify network connectivity to database server
3. Ensure read-only user has proper permissions
4. Check database server firewall settings

### Tool Issues
1. Verify tools are listed in `enabled_tools_json`
2. Check database schema matches tool expectations
3. Review query logs for SQL errors
4. Test individual tools in Django shell

### Performance Issues
1. Add database indexes for frequently queried columns
2. Limit query result sizes with LIMIT clauses
3. Monitor connection pooling
4. Consider read replicas for high-traffic customers

## Example Configurations

### Local Development
```json
{
    "host": "localhost",
    "name": "customer_dev_db",
    "user": "dev_readonly",
    "password": "dev_password",
    "port": 3306
}
```

### Production
```json
{
    "host": "prod-db-cluster.company.com", 
    "name": "customer_production_db",
    "user": "prod_readonly_user",
    "password": "complex_secure_password",
    "port": 3306,
    "charset": "utf8mb4"
}
```

### Cloud Database (AWS RDS)
```json
{
    "host": "customer-db.cluster-xyz.us-east-1.rds.amazonaws.com",
    "name": "customer_business",
    "user": "readonly_user", 
    "password": "aws_secure_password",
    "port": 3306
}
```
