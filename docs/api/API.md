# SAIA API Documentation

## AI Assistant Tools

### ProductAI Assistant (Admin Users)

#### Product Management
- `get_products(limit=20)` - Get all products with company filtering
- `create_product(name, type, expiration, quantity=0.0, price=0.0)` - Create new product
- `update_product(product_id, **kwargs)` - Update existing product
- `delete_product(product_id)` - Delete product

#### Company Management
- `get_companies(limit=20)` - Get all companies
- `create_company(name, email, phone, ...)` - Create new company
- `get_company_details(company_id)` - Get company details

#### Invoice Management
- `get_invoices(limit=20)` - Get all invoices
- `create_invoice(...)` - Create new invoice
- `get_invoice_details(invoice_id)` - Get invoice details

#### Client Data Access
- `execute_client_query(sql_query)` - Execute safe SQL on client database
- `get_client_sample_data(table_name, limit=5)` - Get sample data from client table
- `get_customer_orders(customer_id=None)` - Get customer orders
- `get_customer_sales_summary(start_date=None, end_date=None)` - Get sales summary

### CustomerDataAI Assistant (Customer Users)

#### Database Connection
- `test_customer_database_connection()` - Test database connectivity
- `list_customer_tables()` - List all available tables
- `describe_customer_table(table_name)` - Get table schema

#### Invoice Operations
- `get_all_invoices(limit=50)` - Get all invoices
- `get_latest_invoice()` - Get most recent invoice
- `get_invoice_count()` - Get total invoice count
- `get_invoice_by_number(invoice_number)` - Get specific invoice

#### Contact Management
- `get_contacts(limit=20)` - Get all contacts/customers

#### Data Analysis
- `get_customer_table_sample(table_name, limit=5)` - Get sample data
- `count_customer_table_rows(table_name)` - Count rows in table
- `search_customer_data(table_name, search_column, search_value, limit=10)` - Search data
- `get_database_overview()` - Get database overview with table counts

## Database Services

### ClientDataService

#### Methods
- `execute_safe_query(query, params=None)` - Execute read-only SQL queries
- `get_sample_data(table_name, limit=5)` - Get sample data from table
- `get_table_schema(table_name)` - Get table structure
- `list_tables()` - List all tables in database

#### Security Features
- Only SELECT queries allowed
- Parameterized query support
- Keyword filtering for dangerous operations
- User context tracking for audit logs

## Permission System

### AI Assistant Permissions
- `ai_assistant_can_run_assistant(assistant_cls, user)` - Check if user can run assistant
- `ai_assistant_can_create_thread(user)` - Check thread creation permission
- `ai_assistant_can_view_thread(user, thread)` - Check thread view permission

### Model Permissions
- `can_view_product(user)` - Product view permission
- `can_add_product(user)` - Product creation permission
- `can_change_product(user)` - Product modification permission
- `can_delete_product(user)` - Product deletion permission

Similar patterns for Company, Invoice, Transaction, and other models.

## Database Router

### SAIADatabaseRouter

Routes database operations based on app labels:
- **System Apps**: `admin`, `auth`, `contenttypes`, `sessions`, `users`, `product`, `company`, `invoice`, `project`
- **Default Database**: PostgreSQL for system data
- **Client Database**: MySQL for customer data

#### Methods
- `db_for_read(model)` - Determine read database
- `db_for_write(model)` - Determine write database
- `allow_relation(obj1, obj2)` - Allow cross-database relations
- `allow_migrate(db, app_label)` - Control migration targets

## Error Handling

### Common Error Responses
```json
{
    "status": "error",
    "error": "Error message",
    "message": "User-friendly message"
}
```

### Success Responses
```json
{
    "status": "success",
    "data": {...},
    "count": 10,
    "message": "Operation completed successfully"
}
```

## Security Considerations

### SQL Injection Prevention
- All queries use parameterized statements
- Keyword filtering blocks dangerous operations
- Query validation before execution

### Access Control
- Context separation between admin and customer users
- Company-based data filtering
- Read-only access for customer database

### Audit Logging
- All database operations logged with user context
- Error tracking and monitoring
- Phoenix observability integration

## Rate Limiting

### AI Assistant Calls
- Tool concurrency limited to 1 per assistant
- Recursion limit set to 10 levels
- Temperature set to 0.3 for consistent responses

### Database Queries
- Query timeout limits
- Connection pooling
- Resource usage monitoring
