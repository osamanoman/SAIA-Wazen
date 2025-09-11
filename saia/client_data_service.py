"""
Client Data Source Service

This service provides safe, read-only access to client's database.
It uses raw SQL queries to avoid any risk of modifying client data.
"""

from django.db import connections
from django.conf import settings
import logging
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)


class ClientDataService:
    """
    Service class for safely querying client's database.
    All operations are read-only to protect client data.
    """

    def __init__(self, user=None):  # NEW: Accept user parameter
        self.db_alias = 'client_data'
        self.user = user  # NEW: Store user context
        self.custom_connection = None  # For company-specific database connections
        self._load_company_database_config()

    def _load_company_database_config(self):
        """Load company-specific database configuration if available"""
        if not (self.user and hasattr(self.user, 'company') and self.user.company):
            logger.info("No company context - using default database connection")
            return

        company = self.user.company
        db_config = company.database_config_json

        if not db_config or not isinstance(db_config, dict):
            logger.info(f"No custom database config for {company.name} - using default connection")
            return

        # Validate required fields for custom database connection
        required_fields = ['host', 'name', 'user']
        if not all(field in db_config for field in required_fields):
            logger.warning(f"Incomplete database config for {company.name} - missing required fields")
            return

        logger.info(f"Loading custom database configuration for {company.name}")
        self.custom_db_config = db_config

    def get_connection(self):
        """Get database connection to client data source (default or company-specific)."""
        # Use company-specific connection if available
        if hasattr(self, 'custom_db_config') and self.custom_db_config:
            return self._get_custom_connection()

        # Fall back to default connection
        try:
            return connections[self.db_alias]
        except Exception as e:
            logger.error(f"Failed to connect to default client database: {e}")
            raise

    def _get_custom_connection(self):
        """Get custom database connection for company-specific database"""
        if self.custom_connection:
            # Reuse existing connection if still valid
            try:
                self.custom_connection.ping(reconnect=True)
                return self.custom_connection
            except:
                self.custom_connection = None

        # Create new custom connection
        try:
            config = self.custom_db_config
            self.custom_connection = mysql.connector.connect(
                host=config['host'],
                database=config['name'],
                user=config['user'],
                password=config.get('password', ''),
                port=config.get('port', 3306),
                charset=config.get('charset', 'utf8mb4'),
                autocommit=True,  # For read-only operations
                connection_timeout=10,
                sql_mode='TRADITIONAL',  # Strict mode for safety
            )

            company_name = self.user.company.name if self.user.company else "Unknown"
            logger.info(f"Successfully connected to custom database for {company_name}")
            return self.custom_connection

        except Error as e:
            logger.error(f"Failed to connect to custom database for {self.user.company.name}: {e}")
            # Fall back to default connection
            return connections[self.db_alias]
    
    def execute_safe_query(self, query, params=None):
        """
        Execute a safe, read-only query on client database.

        Args:
            query (str): SQL SELECT query (must start with SELECT, SHOW, or DESCRIBE)
            params (list): Query parameters for safe parameterized queries

        Returns:
            list: Query results as list of dictionaries
        """
        # Security check: only allow SELECT, SHOW, and DESCRIBE queries
        query_upper = query.strip().upper()
        allowed_starts = ['SELECT', 'SHOW', 'DESCRIBE']
        if not any(query_upper.startswith(start) for start in allowed_starts):
            raise ValueError("Only SELECT, SHOW, and DESCRIBE queries are allowed on client database")
        
        # Additional security: block dangerous keywords at statement level
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        # Split query into statements and check each statement start
        statements = [stmt.strip() for stmt in query_upper.split(';') if stmt.strip()]
        for statement in statements:
            for keyword in dangerous_keywords:
                if statement.startswith(keyword + ' ') or statement == keyword:
                    raise ValueError(f"Query contains forbidden keyword: {keyword}")

        # NEW: Log query with user context
        if self.user:
            logger.info(f"Client DB query by user {self.user.username} (company: {self.user.company}): {query}")

        try:
            connection = self.get_connection()

            # Handle custom MySQL connection differently from Django connection
            if hasattr(self, 'custom_db_config') and self.custom_db_config and connection == self.custom_connection:
                return self._execute_custom_query(connection, query, params)
            else:
                return self._execute_django_query(connection, query, params)

        except Exception as e:
            logger.error(f"Error executing client database query: {e}")
            raise

    def _execute_django_query(self, connection, query, params):
        """Execute query using Django database connection"""
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            columns = [col[0] for col in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results

    def _execute_custom_query(self, connection, query, params):
        """Execute query using custom MySQL connection"""
        cursor = connection.cursor(dictionary=True)  # MySQL connector returns dict directly
        try:
            cursor.execute(query, params or [])
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
    
    def get_table_info(self, table_name):
        """
        Get information about a table structure in client MySQL database.

        Args:
            table_name (str): Name of the table

        Returns:
            list: Table column information
        """
        # SECURITY: Use whitelist to prevent SQL injection
        ALLOWED_TABLES = {
            # Core business tables currently used by AI assistants
            'invoices', 'contacts', 'companies', 'products',
            # Common business tables that might be expected
            'customers', 'orders', 'transactions', 'payments',
            'services', 'users', 'accounts', 'inventory',
            'sales', 'purchases', 'suppliers', 'categories',
            # Additional tables for comprehensive business support
            'projects', 'tasks', 'employees', 'departments',
            'reports', 'logs', 'settings', 'configurations'
        }

        # Normalize table name (lowercase, strip whitespace)
        clean_table_name = table_name.strip().lower()

        if not clean_table_name:
            raise ValueError("Table name cannot be empty")

        if clean_table_name not in ALLOWED_TABLES:
            logger.warning(f"Attempted access to unauthorized table: {table_name} by user: {getattr(self.user, 'username', 'Unknown')}")
            raise ValueError(f"Table '{table_name}' is not authorized for access. Allowed tables: {', '.join(sorted(ALLOWED_TABLES))}")

        # Log authorized access for security monitoring
        logger.info(f"Authorized table info access: {clean_table_name} by user: {getattr(self.user, 'username', 'Unknown')}")

        # Use the cleaned table name in query
        query = f"DESCRIBE {clean_table_name}"
        return self.execute_safe_query(query)
    

    
    def get_sample_data(self, table_name, limit=5):
        """
        Get sample data from a client table.

        Args:
            table_name (str): Name of the table
            limit (int): Number of rows to return (default: 5)

        Returns:
            list: Sample data from the table
        """
        # SECURITY: Use same whitelist as get_table_info to prevent SQL injection
        ALLOWED_TABLES = {
            # Core business tables currently used by AI assistants
            'invoices', 'contacts', 'companies', 'products',
            # Common business tables that might be expected
            'customers', 'orders', 'transactions', 'payments',
            'services', 'users', 'accounts', 'inventory',
            'sales', 'purchases', 'suppliers', 'categories',
            # Additional tables for comprehensive business support
            'projects', 'tasks', 'employees', 'departments',
            'reports', 'logs', 'settings', 'configurations'
        }

        # Normalize table name (lowercase, strip whitespace)
        clean_table_name = table_name.strip().lower()

        if not clean_table_name:
            raise ValueError("Table name cannot be empty")

        if clean_table_name not in ALLOWED_TABLES:
            logger.warning(f"Attempted access to unauthorized table: {table_name} by user: {getattr(self.user, 'username', 'Unknown')}")
            raise ValueError(f"Table '{table_name}' is not authorized for access. Allowed tables: {', '.join(sorted(ALLOWED_TABLES))}")

        # Validate and sanitize limit parameter
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            raise ValueError("Limit must be a valid integer")

        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        # Log authorized access for security monitoring
        logger.info(f"Authorized sample data access: {clean_table_name} (limit: {limit}) by user: {getattr(self.user, 'username', 'Unknown')}")

        # Use the cleaned table name in query
        query = f"SELECT * FROM {clean_table_name} LIMIT %s"
        return self.execute_safe_query(query, [limit])

    def list_tables(self):
        """
        List all tables in the client database.

        Returns:
            list: List of table names
        """
        try:
            query = "SHOW TABLES"
            results = self.execute_safe_query(query)
            # MySQL returns table names in a dict with key like 'Tables_in_dbname'
            if results:
                table_key = list(results[0].keys())[0]
                return [row[table_key] for row in results]
            return []
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise

    def describe_table(self, table_name):
        """
        Get table structure/schema information.

        Args:
            table_name (str): Name of the table

        Returns:
            list: Table schema information
        """
        # Validate table name to prevent SQL injection
        if not table_name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Invalid table name")

        try:
            query = f"DESCRIBE {table_name}"
            return self.execute_safe_query(query)
        except Exception as e:
            logger.error(f"Error describing table {table_name}: {e}")
            raise
    
    def test_connection(self):
        """
        Test connection to client database.
        
        Returns:
            dict: Connection status and basic info
        """
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                
            return {
                'status': 'connected',
                'database_version': version,
                'database_name': connection.settings_dict['NAME'],
                'host': connection.settings_dict['HOST'],
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
