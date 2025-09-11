"""
Template for generating company-specific AI assistants.

This template is used to automatically create new AI assistant files
when companies are added to the system.
"""

COMPANY_ASSISTANT_TEMPLATE = '''"""
{company_name} Company AI Assistant

Dedicated AI assistant for {company_name} company with their specific tools and configuration.
Complete isolation from other companies.
"""

import json
import logging
from django_ai_assistant import AIAssistant, method_tool

from saia.base_ai_assistant import SAIAAIAssistantMixin
from saia.client_data_service import ClientDataService
from saia.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class {class_name}AIAssistant(SAIAAIAssistantMixin, AIAssistant):
    """
    Dedicated AI Assistant for {company_name} company.
    Complete isolation from other companies.
    """

    id = "{assistant_id}"
    name = "{company_name} Business Assistant"
    instructions = """
🏢 **{company_name} Business Assistant**

I am your dedicated AI assistant for {company_name} company. I specialize in {activity_name} and help you analyze:

- 📊 Business data and analytics
- 💰 Financial information and invoices
- 👥 Customer and client management
- 📈 Performance metrics and insights

I have access to your {company_name} business database and provide insights about:
- Business invoices and transactions
- Customer analytics and trends
- Performance metrics and KPIs
- Database overview and structure

All operations are read-only to ensure your data security.

**IMPORTANT GUIDELINES:**
1. Use tools ONLY when necessary to answer the user's question
2. After using a tool, provide a clear, final answer to the user
3. Do NOT call multiple tools unnecessarily or repeatedly
4. If you don't have enough information, ask the user for clarification instead of using more tools
5. Always provide a direct answer after using tools - do not continue searching
6. Limit tool usage to maximum 2-3 tools per response

How can I help you analyze your {company_name} business today?
"""

    def __init__(self, **kwargs):
        # Store user from kwargs before calling super()
        self._temp_user = kwargs.get('_user')

        super().__init__(**kwargs)

        # Ensure _user is properly set (fallback to _temp_user if needed)
        if not hasattr(self, '_user') or not self._user:
            self._user = self._temp_user

        # Initialize client data service with user context
        user = getattr(self, '_user', None)
        self.client_service = ClientDataService(user=user)

        # Initialize knowledge service lazily (will be created when first accessed)
        self._knowledge_service = None

        # Verify user belongs to {company_name} company
        if not self._verify_{company_slug}_user():
            raise PermissionError("This AI assistant is only available for {company_name} company users")

    @property
    def knowledge_service(self):
        """Lazy initialization of knowledge service with current user context"""
        if self._knowledge_service is None:
            current_user = getattr(self, '_user', None)
            self._knowledge_service = KnowledgeService(user=current_user)
        return self._knowledge_service

    def _verify_{company_slug}_user(self):
        """Verify that the user belongs to {company_name} company"""
        user = getattr(self, '_user', None)

        if not (user and hasattr(user, 'company') and user.company):
            logger.warning(f"User {{user.username if user else 'Unknown'}} has no company")
            return False

        user_company = user.company.name
        is_{company_slug} = user_company == '{company_name}'
        logger.info(f"User {{user.username}} company: {{user_company}}, is_{company_slug}: {{is_{company_slug}}}")
        return is_{company_slug}

    @method_tool
    def get_{company_slug}_invoices(self, limit: int = 30) -> str:
        """Get invoices for {company_name} company."""
        try:
            query = """
            SELECT
                id, invoice_number, customer_id, amount,
                status, due_date, created_at
            FROM invoices
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            results = self.client_service.execute_safe_query(query, [limit])
            
            return json.dumps({{
                "status": "success",
                "company": "{company_name}",
                "invoices": results,
                "count": len(results),
                "message": f"Retrieved {{len(results)}} {company_name} invoices"
            }}, default=str)
            
        except Exception as e:
            logger.error(f"Failed to get {company_name} invoices: {{e}}")
            return json.dumps({{
                "status": "error",
                "company": "{company_name}",
                "error": str(e),
                "message": "Failed to retrieve {company_name} invoices"
            }})

    @method_tool
    def get_{company_slug}_clients(self, limit: int = 15) -> str:
        """Get clients for {company_name} company."""
        try:
            query = """
            SELECT
                id, name, email, phone, company_id, created_at
            FROM contacts
            ORDER BY name
            LIMIT %s
            """
            
            results = self.client_service.execute_safe_query(query, [limit])
            
            return json.dumps({{
                "status": "success",
                "company": "{company_name}",
                "clients": results,
                "count": len(results),
                "message": f"Retrieved {{len(results)}} {company_name} clients"
            }}, default=str)
            
        except Exception as e:
            logger.error(f"Failed to get {company_name} clients: {{e}}")
            return json.dumps({{
                "status": "error",
                "company": "{company_name}",
                "error": str(e),
                "message": "Failed to retrieve {company_name} clients"
            }})

    @method_tool
    def get_{company_slug}_overview(self) -> str:
        """Get business overview for {company_name} company."""
        try:
            overview_queries = [
                ("invoices", "SELECT COUNT(*) as count FROM invoices"),
                ("clients", "SELECT COUNT(*) as count FROM contacts"),
                ("companies", "SELECT COUNT(*) as count FROM companies")
            ]
            
            overview = {{}}
            for metric_name, query in overview_queries:
                try:
                    result = self.client_service.execute_safe_query(query)
                    overview[metric_name] = result[0]['count'] if result else 0
                except Exception as e:
                    logger.warning(f"Could not get {{metric_name}}: {{e}}")
                    overview[metric_name] = 0
            
            return json.dumps({{
                "status": "success",
                "company": "{company_name}",
                "overview": overview,
                "message": "{company_name} business overview retrieved successfully"
            }})
            
        except Exception as e:
            logger.error(f"Failed to get {company_name} overview: {{e}}")
            return json.dumps({{
                "status": "error",
                "company": "{company_name}",
                "error": str(e),
                "message": "Failed to get {company_name} overview"
            }})

    @method_tool
    def analyze_{company_slug}_performance(self) -> str:
        """Analyze business performance for {company_name}."""
        try:
            query = """
            SELECT
                COUNT(*) as total_invoices,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_invoice_value
            FROM invoices
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """

            results = self.client_service.execute_safe_query(query)
            performance = results[0] if results else {{}}

            return json.dumps({{
                "status": "success",
                "company": "{company_name}",
                "performance_metrics": {{
                    "total_invoices": performance.get('total_invoices', 0),
                    "total_revenue": float(performance.get('total_revenue', 0)) if performance.get('total_revenue') else 0,
                    "avg_invoice_value": float(performance.get('avg_invoice_value', 0)) if performance.get('avg_invoice_value') else 0
                }},
                "period": "Last 30 days",
                "message": "{company_name} performance analysis completed successfully"
            }}, default=str)

        except Exception as e:
            logger.error(f"Failed to analyze {company_name} performance: {{e}}")
            return json.dumps({{
                "status": "error",
                "company": "{company_name}",
                "error": str(e),
                "message": "Failed to analyze {company_name} performance"
            }})

    @method_tool
    def search_{company_slug}_knowledge(self, query: str, limit: int = 10) -> str:
        """Search {company_name} company knowledge base for information."""
        try:
            results = self.knowledge_service.search_knowledge(query, limit=limit)

            if not results:
                return json.dumps({{
                    "status": "success",
                    "company": "{company_name}",
                    "results": [],
                    "count": 0,
                    "message": f"No knowledge base results found for query: {{query}}"
                }})

            # Format results for better readability
            formatted_results = []
            for result in results:
                formatted_results.append({{
                    "title": result.get('title', 'Untitled'),
                    "content": result.get('content', '')[:500] + ('...' if len(result.get('content', '')) > 500 else ''),
                    "type": result.get('type', 'unknown'),
                    "category": result.get('category', 'General')
                }})

            return json.dumps({{
                "status": "success",
                "company": "{company_name}",
                "results": formatted_results,
                "count": len(results),
                "message": f"Found {{len(results)}} knowledge base results for: {{query}}"
            }}, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to search {company_name} knowledge: {{e}}")
            return json.dumps({{
                "status": "error",
                "company": "{company_name}",
                "error": str(e),
                "message": f"Failed to search {company_name} knowledge base"
            }})

    @method_tool
    def get_{company_slug}_company_info(self) -> str:
        """Get comprehensive information about {company_name} company."""
        try:
            # Search for company information in knowledge base
            company_queries = [
                "عن {company_name}",
                "من هي {company_name}",
                "about {company_name}",
                "company information",
                "من نحن"
            ]

            all_results = []
            for query in company_queries:
                results = self.knowledge_service.search_knowledge(query, limit=3)
                all_results.extend(results)

            # Remove duplicates and get top results
            seen_titles = set()
            unique_results = []
            for result in all_results:
                title = result.get('title', '')
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_results.append(result)
                    if len(unique_results) >= 5:
                        break

            if not unique_results:
                return json.dumps({{
                    "status": "success",
                    "company": "{company_name}",
                    "info": [],
                    "message": "No company information found in knowledge base"
                }})

            # Format company information
            company_info = []
            for result in unique_results:
                company_info.append({{
                    "title": result.get('title', 'Company Information'),
                    "content": result.get('content', ''),
                    "type": result.get('type', 'info')
                }})

            return json.dumps({{
                "status": "success",
                "company": "{company_name}",
                "info": company_info,
                "count": len(company_info),
                "message": f"Retrieved comprehensive {company_name} company information"
            }}, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to get {company_name} company info: {{e}}")
            return json.dumps({{
                "status": "error",
                "company": "{company_name}",
                "error": str(e),
                "message": f"Failed to retrieve {company_name} company information"
            }})
'''


def generate_company_assistant(company_name, activity_name="business operations"):
    """
    Generate a company-specific AI assistant file content.
    
    Args:
        company_name (str): Name of the company
        activity_name (str): Company's activity/business type
        
    Returns:
        str: Generated Python file content
    """
    # Create safe class name and assistant ID
    class_name = company_name.replace(' ', '').replace('-', '').replace('_', '')
    company_slug = company_name.lower().replace(' ', '_').replace('-', '_')
    assistant_id = f"{company_slug}_ai_assistant"
    
    return COMPANY_ASSISTANT_TEMPLATE.format(
        company_name=company_name,
        class_name=class_name,
        company_slug=company_slug,
        assistant_id=assistant_id,
        activity_name=activity_name
    )
