import json
import os
from datetime import date

from django.conf import settings
from django_ai_assistant import AIAssistant, method_tool

from company.models import Company, Branch
from invoice.models import Invoice, InvoiceDetails, Transaction
from product.models import Product
from saia.base_ai_assistant import SAIAAIAssistantMixin
from saia.client_data_service import ClientDataService
from saia.mixins import CompanyFilterMixin
from saia.permissions import (  # NEW IMPORT
    can_view_product, can_add_product, can_change_product, can_delete_product,
    can_view_company, can_add_company, can_change_company, can_delete_company,
    can_view_invoice, can_add_invoice, can_change_invoice, can_delete_invoice,
    can_view_invoice_details, can_add_invoice_details, can_change_invoice_details, can_delete_invoice_details,
    can_view_transaction, can_add_transaction,
    can_add_branch, can_change_branch, can_delete_branch
)


class ProductAIAssistant(SAIAAIAssistantMixin, AIAssistant, CompanyFilterMixin):
    id = "product_assistant"
    name = "Product Assistant"
    instructions = (
        "You are a business assistant for SAIA Business Management System. "
        "You help users manage products, companies, branches, invoices, and transactions. "
        "\n\nIMPORTANT GUIDELINES:\n"
        "1. Use the provided tools ONLY when necessary to answer the user's question\n"
        "2. After using tools, provide a clear, final answer to the user\n"
        "3. Do NOT call multiple tools unnecessarily\n"
        "4. If you don't have enough information, ask the user for clarification\n"
        "5. Always provide a direct answer after using tools\n"
        "6. Customer users can only access their own company's data\n"  # NEW
        "\nWhen referencing IDs, use format: #<id>\n"
        "Be helpful, concise, and always end with a clear response to the user."
    )

    _user = settings.AUTH_USER_MODEL

    _monthes = {
        "يناير":"01",
        "January":"01",
        "فبراير":"02",
        "February":"02",
        "مارس":"03",
        "March":"03",
        "ابريل":"04",
        "أبريل":"04",
        "إبريل":"04",
        "April":"04",
        "مايو":"05",
        "May":"05",
        "يونيو":"06",
        "June":"06",
        "يوليو":"07",
        "July":"07",
        "أغسطس":"08",
        "اغسطس":"08",
        "August":"08",
        "سبتمر":"09",
        "September":"09",
        "اكتوبر":"10",
        "أكتوبر":"10",
        "October":"10",
        "نوفمبر":"11",
        "November":"11",
        "ديسمبر":"12",
        "December":"12"
    }

    # Client Data Source Methods (Read-Only)
    @method_tool
    def list_client_tables(self) -> str:
        """List all tables available in the client's data source database."""
        try:
            client_service = ClientDataService()
            tables = client_service.list_tables()
            return json.dumps({
                "status": "success",
                "client_tables": tables,
                "message": f"Found {len(tables)} tables in client database"
            }, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Failed to connect to client database"
            })

    @method_tool
    def get_client_table_info(self, table_name: str) -> str:
        """Get structure information about a specific table in client's database."""
        try:
            client_service = ClientDataService()
            table_info = client_service.get_table_info(table_name)
            return json.dumps({
                "status": "success",
                "table_name": table_name,
                "columns": table_info,
                "message": f"Retrieved structure for table: {table_name}"
            }, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "table_name": table_name,
                "error": str(e)
            })

    @method_tool
    def query_client_data(self, sql_query: str) -> str:
        """Execute a safe SELECT query on client's database. Only SELECT queries are allowed."""
        # NEW: Check if customer user has company
        if hasattr(self._user, 'is_customer') and self._user.is_customer and not self._user.company:
            return json.dumps({
                "status": "error",
                "message": "Customer user must be associated with a company to access client data"
            })

        try:
            client_service = ClientDataService(user=self._user)  # Pass user context
            results = client_service.execute_safe_query(sql_query)
            return json.dumps({
                "status": "success",
                "query": sql_query,
                "results": results,
                "count": len(results),
                "message": f"Query executed successfully, returned {len(results)} rows"
            }, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "query": sql_query,
                "error": str(e),
                "message": "Query failed - ensure it's a valid SELECT statement"
            })

    @method_tool
    def get_client_sample_data(self, table_name: str, limit: int = 5) -> str:
        """Get sample data from a client table to understand its structure and content."""
        try:
            client_service = ClientDataService()
            sample_data = client_service.get_sample_data(table_name, limit)
            return json.dumps({
                "status": "success",
                "table_name": table_name,
                "sample_data": sample_data,
                "count": len(sample_data),
                "message": f"Retrieved {len(sample_data)} sample rows from {table_name}"
            }, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "table_name": table_name,
                "error": str(e)
            })

    @method_tool
    def test_client_database_connection(self) -> str:
        """Test connection to client's data source database."""
        try:
            client_service = ClientDataService()
            connection_info = client_service.test_connection()
            return json.dumps(connection_info, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Failed to test client database connection"
            })

    # Customer-Specific Data Tools (Examples - Customize based on customer schema)
    @method_tool
    def list_customer_products(self) -> str:
        """List all products from customer's database."""
        if not can_view_product(self._user):
            return "You don't have permission."

        try:
            client_service = ClientDataService()
            # Adapt this query based on customer's actual table structure
            query = """
            SELECT
                id,
                product_name as name,
                price,
                category,
                stock_quantity,
                created_date
            FROM products
            ORDER BY created_date DESC
            LIMIT 100
            """
            results = client_service.execute_safe_query(query)

            return json.dumps({
                "status": "success",
                "customer_products": results,
                "count": len(results),
                "message": f"Retrieved {len(results)} products from customer database"
            }, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Failed to retrieve customer products"
            })

    @method_tool
    def list_customer_orders(self, customer_id: int = None, limit: int = 50) -> str:
        """List customer orders, optionally filtered by customer ID."""
        if not can_view_invoice(self._user):
            return "You don't have permission."

        try:
            client_service = ClientDataService()

            if customer_id:
                query = """
                SELECT
                    o.order_id,
                    o.customer_id,
                    c.customer_name,
                    o.order_date,
                    o.total_amount,
                    o.status
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.customer_id = %s
                ORDER BY o.order_date DESC
                LIMIT %s
                """
                params = [customer_id, limit]
            else:
                query = """
                SELECT
                    o.order_id,
                    o.customer_id,
                    c.customer_name,
                    o.order_date,
                    o.total_amount,
                    o.status
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                ORDER BY o.order_date DESC
                LIMIT %s
                """
                params = [limit]

            results = client_service.execute_safe_query(query, params)

            return json.dumps({
                "status": "success",
                "customer_orders": results,
                "count": len(results),
                "filter": f"customer_id={customer_id}" if customer_id else "all_customers",
                "message": f"Retrieved {len(results)} orders from customer database"
            }, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Failed to retrieve customer orders"
            })

    @method_tool
    def get_customer_sales_summary(self, start_date: str = None, end_date: str = None) -> str:
        """Get sales summary from customer database for a date range."""
        if not can_view_transaction(self._user):
            return "You don't have permission."

        try:
            client_service = ClientDataService()

            # Build dynamic query based on date filters
            base_query = """
            SELECT
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as average_order_value,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM orders
            WHERE 1=1
            """

            params = []
            if start_date:
                base_query += " AND order_date >= %s"
                params.append(start_date)
            if end_date:
                base_query += " AND order_date <= %s"
                params.append(end_date)

            results = client_service.execute_safe_query(base_query, params)

            return json.dumps({
                "status": "success",
                "sales_summary": results[0] if results else {},
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "message": "Sales summary retrieved successfully"
            }, default=str)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Failed to retrieve sales summary"
            })

    @method_tool
    def get_current_user_email(self):
        """ Get the Email of the current user"""
        return self._user.email

    @method_tool
    def assign_company_to_branch(self, branch_id: int, company_id: int) -> str:
        """Assign a company to a branch.
        Set the `company_id` param to a company id."""
        try:
            branch = Branch.objects.get(id=branch_id)
            if company_id:
                company = Company.objects.get(id=company_id)
            else:
                company = None
        except Branch.DoesNotExist:
            return f"ERROR: Branch {branch_id} does not exist"
        except Company.DoesNotExist:
            return f"ERROR: Company {company_id} does not exist"
        branch.company_id = company
        branch.save()
        return f"Assigned {company_id} to branch #{branch.id} - {branch.name}"

    @method_tool
    def assign_company_to_invoice(self, invoice_id: int, company_id: int) -> str:
        """Assign a company to an invoice.
        Set the `company_id` param to a company id."""
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            if company_id:
                company = Company.objects.get(id=company_id)
            else:
                company = None
        except Invoice.DoesNotExist:
            return f"ERROR: Invoice {invoice_id} does not exist"
        except Company.DoesNotExist:
            return f"ERROR: Company {company_id} does not exist"
        invoice.company_id = company
        invoice.save()
        return f"Assigned {company_id} to invoice #{invoice.id} - {invoice.number}"

    @method_tool
    def assign_invoice_to_invoice_details(self, invoicedetails_id: int, invoice_id: int) -> str:
        """Assign an invoice to an invoice details.
        Set the `invoice_id` param to a invoice id."""
        try:
            invoice_details = InvoiceDetails.objects.get(id=invoicedetails_id)
            if invoice_id:
                invoice = Invoice.objects.get(id=invoice_id)
            else:
                invoice = None
        except InvoiceDetails.DoesNotExist:
            return f"ERROR: Invoice Details {invoicedetails_id} does not exist"
        except Invoice.DoesNotExist:
            return f"ERROR: Invoice {invoice_id} does not exist"
        invoice_details.invoice_id = invoice
        invoice_details.save()
        return f"Assigned invoice {invoice_id} to invoice details #{invoice_details.id}"

    @method_tool
    def assign_product_to_invoice_details(self, invoicedetails_id: int, product_id: int) -> str:
        """Assign a product to an invoice details. Set the `product_id` param to a product id."""
        try:
            invoice_details = InvoiceDetails.objects.get(id=invoicedetails_id)
            if product_id:
                product = Product.objects.get(id=product_id)
            else:
                product = None
        except InvoiceDetails.DoesNotExist:
            return f"ERROR: Invoice Details {invoicedetails_id} does not exist"
        except Product.DoesNotExist:
            return f"ERROR: Product {product_id} does not exist"
        invoice_details.product_id = product
        invoice_details.save()
        return f"Assigned product {product_id} to invoice details #{invoice_details.id}"

    @method_tool
    def list_transactions(self) -> str:
        """Show all transactions as an HTML table."""
        if can_view_transaction(self._user):
            return json.dumps(
                {
                    "transactions": list(
                        Transaction.objects.values()
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_transactions_by_months(self, month_name: str) -> str:
        """Show all transactions according to month in transaction_date as an HTML table."""
        if can_view_transaction(self._user):
            if month_name in self._monthes.keys():
                return json.dumps(
                    {
                        "transactions": list(
                            Transaction.objects.filter(transaction_date__month=self._monthes[month_name]).values()
                        ),
                    }
                    , default=str)
            else:
                return f"{month_name} is not correct."
        else:
            return "You don't have permission."

    @method_tool
    def list_transactions_by_years(self, year: int) -> str:
        """Show all transactions according to year in transaction_date as an HTML table."""
        if can_view_transaction(self._user):
            return json.dumps(
                {
                    "transactions": list(
                        Transaction.objects.filter(transaction_date__year=year).values()
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_transactions_by_months_and_years(self, month_name: str, year: int) -> str:
        """Show all transactions according to month and year in transaction_date as an HTML table."""
        if can_view_transaction(self._user):
            if month_name in self._monthes.keys():
                return json.dumps(
                    {
                        "transactions": list(
                            Transaction.objects.filter(transaction_date__month=self._monthes[month_name], transaction_date__year=year).values()
                        ),
                    }
                    , default=str)
            else:
                return f"{month_name} is not correct."
        else:
            return "You don't have permission."


    @method_tool
    def list_product(self, product_id: int) -> str:
        """List single product"""
        if can_view_product(self._user):
            return json.dumps(
                {
                    "product": list(
                        Product.objects.filter(id=product_id).values("id", "name", "price", "type", "quantity",
                                                                     "expiration")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_products(self) -> str:
        """List all products as a table"""
        if can_view_product(self._user):
            # NEW: Use company-filtered queryset
            products = self.get_company_filtered_queryset(Product)
            return json.dumps(
                {
                    "products": list(
                        products.values("id", "name", "price", "type", "quantity", "expiration", "company")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def get_company_details(self, company_id: int) -> str:
        """Get company details - alias for list_company for backward compatibility"""
        return self.list_company(company_id)

    @method_tool
    def list_company(self, company_id: int) -> str:
        """List single company"""
        if can_view_company(self._user):
            return json.dumps(
                {
                    "company": list(
                        Company.objects.filter(id=company_id).values("id", "name", "email", "phone", "activity_name",
                                                                     "activity_type",
                                                                     "activity_status", "subscription_start_date",
                                                                     "subscription_end_date",
                                                                     "subscription_status")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def get_companies(self) -> str:
        """Get all companies - alias for list_companies for backward compatibility"""
        return self.list_companies()

    @method_tool
    def list_companies(self) -> str:
        """List all companies"""
        if can_view_company(self._user):
            # NEW: Customer users can only see their own company
            if hasattr(self._user, 'is_customer') and self._user.is_customer and self._user.company:
                companies = Company.objects.filter(id=self._user.company.id)
            else:
                companies = Company.objects.all()

            return json.dumps(
                {
                    "companies": list(
                        companies.values("id", "name", "email", "phone", "activity_name", "activity_type",
                                               "activity_status", "subscription_start_date", "subscription_end_date",
                                               "subscription_status")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_invoice(self, invoice_id: int) -> str:
        """List single invoice"""
        if can_view_invoice(self._user):
            return json.dumps(
                {
                    "invoice": list(
                        Invoice.objects.filter(id=invoice_id).values("id", "number", "company", "price", "issue_date", "print_date")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_invoices(self) -> str:
        """List all invoices"""
        if can_view_invoice(self._user):
            # NEW: Use company-filtered queryset
            invoices = self.get_company_filtered_queryset(Invoice)
            return json.dumps(
                {
                    "invoices": list(
                        invoices.values("id", "number", "company", "price", "issue_date", "print_date")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_invoice_detail(self, invoicedetails_id: int) -> str:
        """List Single invoice detail"""
        if can_view_invoice_details(self._user):
            return json.dumps(
                {
                    "invoice_detail": list(
                        InvoiceDetails.objects.filter(id=invoicedetails_id).values("id", "invoice", "product", "quantity", "product_price",
                                                      "discount_percentage", "total_without_tax", "tax_price",
                                                      "total_with_tax")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_invoice_details(self) -> str:
        """List all invoice details"""
        if can_view_invoice_details(self._user):
            return json.dumps(
                {
                    "invoice_details": list(
                        InvoiceDetails.objects.values("id", "invoice", "product", "quantity", "product_price",
                                                      "discount_percentage", "total_without_tax", "tax_price",
                                                      "total_with_tax")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_invoice_with_its_invoice_details(self, invoice_id: int) -> str:
        """List single invoice with its invoice details"""
        if can_view_invoice(self._user) and can_view_invoice_details(self._user):
            return json.dumps(
                {
                    "invoice": list(
                        Invoice.objects.filter(id=invoice_id).values("id", "number", "company", "price", "issue_date", "print_date")
                    ),
                    "invoice_details": list(
                        InvoiceDetails.objects.filter(invoice_id=invoice_id).values("id", "invoice", "product", "quantity", "product_price",
                                                      "discount_percentage", "total_without_tax", "tax_price",
                                                      "total_with_tax")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def list_invoices_with_invoice_details(self) -> str:
        """List all invoices with invoice details"""
        if can_view_invoice(self._user) and can_view_invoice_details(self._user):
            return json.dumps(
                {
                    "invoices": list(
                        Invoice.objects.values("id", "number", "company", "price", "issue_date", "print_date")
                    ),
                    "invoice_details": list(
                        InvoiceDetails.objects.values("id", "invoice", "product", "quantity", "product_price",
                                                      "discount_percentage", "total_without_tax", "tax_price",
                                                      "total_with_tax")
                    ),
                }
                , default=str)
        else:
            return "You don't have permission."

    @method_tool
    def count_products(self) -> str:
        """Count all products."""
        if can_view_product(self._user):
            p = Product.objects.all().count()
            return f"The Products count: #{p}."
        else:
            return "You don't have permission."

    @method_tool
    def count_companies(self) -> str:
        """Count all companies."""
        if can_view_company(self._user):
            company = Company.objects.all().count()
            return f"The Companies count: #{company}."
        else:
            return "You don't have permission."

    @method_tool
    def count_branches(self) -> str:
        """Count all branches."""
        if can_view_company(self._user):
            branch = Branch.objects.all().count()
            return f"The Branches count: #{branch}."
        else:
            return "You don't have permission."

    @method_tool
    def count_invoices(self) -> str:
        """Count all invoices."""
        if can_view_invoice(self._user):
            invoice = Invoice.objects.all().count()
            return f"The Invoices count: #{invoice}"
        else:
            return "You don't have permission."

    @method_tool
    def count_invoice_details(self) -> str:
        """Count all invoice details."""
        if can_view_invoice_details(self._user):
            invoice_details = InvoiceDetails.objects.all().count()
            return f"The Invoices Details count: #{invoice_details}"
        else:
            return "You don't have permission."

    @method_tool
    def create_transaction(self, product_id: int, price: float, transaction_date: date) -> str:
        """Create a new transaction."""
        if can_add_transaction(self._user):
            if product_id:
                try:
                    assign_product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return f"ERROR: Product #{product_id} does not exist"
            else:
                assign_product = None
            transaction = Transaction.objects.create(product=assign_product, price=price, transaction_date=transaction_date)
            return f"Created Transaction #{transaction.id}"
        else:
            return "You don't have permission."

    @method_tool
    def create_product(self, name: str, type: str, expiration: date, quantity: float = 0.0, price: float = 0.0) -> str:
        """Create a new product."""
        if can_add_product(self._user):
            # NEW: Auto-assign company for customer users
            company = None
            if hasattr(self._user, 'is_customer') and self._user.is_customer and self._user.company:
                company = self._user.company

            p = Product.objects.create(
                name=name,
                price=price,
                type=type,
                expiration=expiration,
                quantity=quantity,
                company=company  # NEW
            )
            return f"Created Product #{p.id} - {p.name}"
        else:
            return "You don't have permission."

    @method_tool
    def create_company(self, name: str, email: str, phone: int, activity_name: str, activity_type: str,
                       activity_status: str, subscription_start_date: date, subscription_end_date: date,
                       subscription_status: str) -> str:
        """Create a new company."""
        if can_add_company(self._user):
            company = Company.objects.create(name=name, email=email, phone=phone, activity_name=activity_name,
                                             activity_type=activity_type, activity_status=activity_status,
                                             subscription_start_date=subscription_start_date,
                                             subscription_end_date=subscription_end_date,
                                             subscription_status=subscription_status)
            return f"Created Company #{company.id} - {company.name}"
        else:
            return "You don't have permission."

    @method_tool
    def create_branch(self, company_id: int, name: str, address: str, status: str) -> str:
        """Create a new branch."""
        if can_add_branch(self._user):
            if company_id:
                try:
                    assign_company = Company.objects.get(id=company_id)
                except Company.DoesNotExist:
                    return f"ERROR: Company #{company_id} does not exist"
            else:
                assign_company = None

            branch = Branch.objects.create(company=assign_company, name=name, address=address, status=status)
            return f"Created Branch #{branch.id} - {branch.name}"
        else:
            return "You don't have permission."

    @method_tool
    def create_invoice(self, number: int, company_id: int, price: float, issue_date: date,
                       print_date: date) -> str:
        """Create a new invoices.
        Assign it to a company by passing the `company_id` param."""
        if can_add_invoice(self._user):
            if company_id:
                try:
                    company = Company.objects.get(id=company_id)
                except Company.DoesNotExist:
                    return f"ERROR: Company #{company_id} does not exist"
            else:
                company = None

            invoice = Invoice.objects.create(number=number, company=company, price=price, issue_date=issue_date,
                                             print_date=print_date)
            return f"Created invoice #{invoice.id} - {invoice.number}"
        else:
            return "You don't have permission."

    @method_tool
    def create_invoice_details(self, invoice_id: int, product_id: int, quantity: float, product_price: float,
                               discount_percentage: float, total_without_tax: float, tax_price: float,
                               total_with_tax: float) -> str:
        """Create a new invoice details.
        Assign invoice to an invoice details by passing the `invoice_id` param."""
        if can_add_invoice_details(self._user):
            if invoice_id:
                try:
                    assign_invoice = Invoice.objects.get(id=invoice_id)
                except Invoice.DoesNotExist:
                    return f"ERROR: Invoice #{invoice_id} does not exist"
            else:
                assign_invoice = None

            if product_id:
                try:
                    assign_product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return f"ERROR: Product #{product_id} does not exist"
            else:
                assign_product = None
            invoice_details = InvoiceDetails.objects.create(invoice=assign_invoice, product=assign_product,
                                                            quantity=quantity,
                                                            product_price=product_price,
                                                            discount_percentage=discount_percentage,
                                                            total_without_tax=total_without_tax, tax_price=tax_price,
                                                            total_with_tax=total_with_tax)
            return f"Created invoice details #{invoice_details.id}"
        else:
            return "You don't have permission."

    @method_tool
    def update_product(self, product_id: int, name: str, type: str, expiration: date, quantity: float = 0.0,
                       price: float = 0.0) -> str:
        """Update a product."""
        if can_change_product(self._user):
            try:
                p = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return f"ERROR: Product {product_id} does not exist"
            p.name = name
            p.price = price
            p.type = type
            p.quantity = quantity
            p.expiration = expiration
            p.save()
            return f"Updated product #{product_id} - {p.name}"
        else:
            return "You don't have permission."

    @method_tool
    def update_company(self, company_id: int, name: str, email: str, phone: int, activity_name: str, activity_type: str,
                       activity_status: str, subscription_start_date: date, subscription_end_date: date,
                       subscription_status: str) -> str:
        """Update a company."""
        if can_change_company(self._user):
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return f"ERROR: Company {company_id} does not exist"
            company.name = name
            company.email = email
            company.phone = phone
            company.activity_name = activity_name
            company.activity_type = activity_type
            company.activity_status = activity_status
            company.subscription_start_date = subscription_start_date
            company.subscription_end_date = subscription_end_date
            company.subscription_status = subscription_status
            company.save()
            return f"Updated company #{company_id} - {company.name}"
        else:
            return "You don't have permission."

    @method_tool
    def update_branch(self, branch_id: int, company_id: str, name: str, address: str, status: str) -> str:
        """Update a branch."""
        if can_change_branch(self._user):
            if company_id:
                try:
                    assign_company = Company.objects.get(id=company_id)
                except Company.DoesNotExist:
                    return f"ERROR: Company #{company_id} does not exist"
            else:
                assign_company = None

            try:
                branch = Branch.get(id=branch_id)
            except Branch.DoesNotExist:
                return f"ERROR: Branch {branch_id} does not exist"

            branch.company = assign_company
            branch.name = name
            branch.address = address
            branch.status = status
            branch.save()

            return f"Updated Branch #{branch.id}"
        else:
            return "You don't have permission."

    @method_tool
    def update_invoice(self, invoice_id: int, number: int, company_id: int, price: float, issue_date: date,
                       print_date: date) -> str:
        """Update a invoice."""
        if can_change_invoice(self._user):
            if company_id:
                try:
                    company = Company.objects.get(id=company_id)
                except Company.DoesNotExist:
                    return f"ERROR: Company #{company_id} does not exist"
            else:
                company = None

            try:
                invoice = Invoice.objects.get(id=invoice_id)
            except Invoice.DoesNotExist:
                return f"ERROR: Invoice {invoice_id} does not exist"

            invoice.number = number
            invoice.company = company
            invoice.price = price
            invoice.issue_date = issue_date
            invoice.print_date = print_date
            invoice.save()

            return f"Updated invoice #{invoice_id} - {invoice.number}"
        else:
            return "You don't have permission."

    @method_tool
    def update_invoice_details(self, invoice_id: int, invoicedetails_id: int, product_id: int, quantity: float,
                               product_price: float,
                               discount_percentage: float, total_without_tax: float, tax_price: float,
                               total_with_tax: float) -> str:
        """Update an invoice details."""
        if can_change_invoice_details(self._user):
            if invoice_id:
                try:
                    assign_invoice = Invoice.objects.get(id=invoice_id)
                except Invoice.DoesNotExist:
                    return f"ERROR: Invoice #{invoice_id} does not exist"
            else:
                assign_invoice = None

            if product_id:
                try:
                    assign_product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return f"ERROR: Product #{product_id} does not exist"
            else:
                assign_product = None

            try:
                invoice_details = InvoiceDetails.get(id=invoicedetails_id)
            except InvoiceDetails.DoesNotExist:
                return f"ERROR: Invoice Details {invoicedetails_id} does not exist"

            invoice_details.invoice = assign_invoice
            invoice_details.product = assign_product
            invoice_details.quantity = quantity
            invoice_details.product_price = product_price
            invoice_details.discount_percentage = discount_percentage
            invoice_details.total_without_tax = total_without_tax
            invoice_details.tax_price = tax_price
            invoice_details.total_with_tax = total_with_tax
            invoice_details.save()
            return f"Updated invoice details #{invoicedetails_id}"
        else:
            return "You don't have permission."

    @method_tool
    def delete_product(self, product_id: int) -> str:
        """Delete a product"""
        if can_delete_product(self._user):
            try:
                p = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return f"ERROR: Product {product_id} does not exist"
            p.delete()
            return f"Deleted Product #{product_id} - {p.title}"
        else:
            return "You don't have permission."

    @method_tool
    def delete_company(self, company_id: int) -> str:
        """Delete a company"""
        if can_delete_company(self._user):
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return f"ERROR: Company {company_id} does not exist"
            company.delete()
            return f"Deleted company #{company_id} - {company.name}"
        else:
            return "You don't have permission."

    @method_tool
    def delete_branch(self, branch_id: int) -> str:
        """Delete a branch"""
        if can_delete_branch(self._user):
            try:
                branch = Branch.objects.get(id=branch_id)
            except Branch.DoesNotExist:
                return f"ERROR: Branch {branch_id} does not exist"
            branch.delete()
            return f"Deleted Branch #{branch_id} - {branch.name}"
        else:
            return "You don't have permission."

    @method_tool
    def delete_invoice(self, invoice_id: int) -> str:
        """Delete a invoice"""
        if can_delete_invoice(self._user):
            try:
                invoice = Invoice.objects.get(id=invoice_id)
            except Invoice.DoesNotExist:
                return f"ERROR: Invoice {invoice_id} does not exist"
            invoice.delete()
            return f"Deleted invoice #{invoice_id} - {invoice.number} with its details"
        else:
            return "You don't have permission."

    @method_tool
    def delete_invoice_details(self, invoicedetails_id: int) -> str:
        """Delete a invoice details"""
        if can_delete_invoice_details(self._user):
            try:
                invoice_details = InvoiceDetails.get(id=invoicedetails_id)
            except InvoiceDetails.DoesNotExist:
                return f"ERROR: Invoice Details {invoicedetails_id} does not exist"
            invoice_details.delete()
            return f"Deleted invoice details #{invoicedetails_id}"
        else:
            return "You don't have permission."
