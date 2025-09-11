"""
Test AI Company Company AI Assistant

Dedicated AI assistant for Test AI Company company with their specific tools and configuration.
Complete isolation from other companies.
"""

import json
import logging
from django_ai_assistant import AIAssistant, method_tool

from saia.base_ai_assistant import SAIAAIAssistantMixin
from saia.client_data_service import ClientDataService
from saia.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class TestAICompanyAIAssistant(SAIAAIAssistantMixin, AIAssistant):
    """
    Dedicated AI Assistant for Test AI Company company.
    Complete isolation from other companies.
    """

    id = "test_ai_company_ai_assistant"
    name = "Test AI Company Business Assistant"
    instructions = """
🏢 **Test AI Company Business Assistant**

I am your dedicated AI assistant for Test AI Company company. I specialize in AI Technology and help you analyze:

- 📊 Business data and analytics
- 💰 Financial information and invoices
- 👥 Customer and client management
- 📈 Performance metrics and insights

I have access to your Test AI Company business database and provide insights about:
- Business invoices and transactions
- Customer analytics and trends
- Performance metrics and KPIs
- Database overview and structure

All operations are read-only to ensure your data security.

How can I help you analyze your Test AI Company business today?
"""

    def __init__(self, **kwargs):
        # Store user from kwargs before calling super()
        self._temp_user = kwargs.get('_user')

        super().__init__(**kwargs)

        # Initialize client data service with user context
        user = getattr(self, '_user', None) or getattr(self, '_temp_user', None)
        self.client_service = ClientDataService(user=user)

        # Initialize knowledge service lazily (will be created when first accessed)
        self._knowledge_service = None

        # Verify user belongs to Test AI Company company
        if not self._verify_test_ai_company_user():
            raise PermissionError("This AI assistant is only available for Test AI Company company users")

    @property
    def knowledge_service(self):
        """Lazy initialization of knowledge service with current user context"""
        if self._knowledge_service is None:
            current_user = getattr(self, '_user', None)
            self._knowledge_service = KnowledgeService(user=current_user)
        return self._knowledge_service

    def _verify_test_ai_company_user(self):
        """Verify that the user belongs to Test AI Company company"""
        user = getattr(self, '_user', None) or getattr(self, '_temp_user', None)

        if not (user and hasattr(user, 'company') and user.company):
            logger.warning(f"User {user.username if user else 'Unknown'} has no company")
            return False

        user_company = user.company.name
        is_test_ai_company = user_company == 'Test AI Company'
        logger.info(f"User {user.username} company: {user_company}, is_test_ai_company: {is_test_ai_company}")
        return is_test_ai_company

    @method_tool
    def get_test_ai_company_invoices(self, limit: int = 30) -> str:
        """Get invoices for Test AI Company company."""
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
            
            return json.dumps({
                "status": "success",
                "company": "Test AI Company",
                "invoices": results,
                "count": len(results),
                "message": f"Retrieved {len(results)} Test AI Company invoices"
            }, default=str)
            
        except Exception as e:
            logger.error(f"Failed to get Test AI Company invoices: {e}")
            return json.dumps({
                "status": "error",
                "company": "Test AI Company",
                "error": str(e),
                "message": "Failed to retrieve Test AI Company invoices"
            })

    @method_tool
    def get_test_ai_company_clients(self, limit: int = 15) -> str:
        """Get clients for Test AI Company company."""
        try:
            query = """
            SELECT
                id, name, email, phone, company_id, created_at
            FROM contacts
            ORDER BY name
            LIMIT %s
            """
            
            results = self.client_service.execute_safe_query(query, [limit])
            
            return json.dumps({
                "status": "success",
                "company": "Test AI Company",
                "clients": results,
                "count": len(results),
                "message": f"Retrieved {len(results)} Test AI Company clients"
            }, default=str)
            
        except Exception as e:
            logger.error(f"Failed to get Test AI Company clients: {e}")
            return json.dumps({
                "status": "error",
                "company": "Test AI Company",
                "error": str(e),
                "message": "Failed to retrieve Test AI Company clients"
            })

    @method_tool
    def get_test_ai_company_overview(self) -> str:
        """Get business overview for Test AI Company company."""
        try:
            overview_queries = [
                ("invoices", "SELECT COUNT(*) as count FROM invoices"),
                ("clients", "SELECT COUNT(*) as count FROM contacts"),
                ("companies", "SELECT COUNT(*) as count FROM companies")
            ]
            
            overview = {}
            for metric_name, query in overview_queries:
                try:
                    result = self.client_service.execute_safe_query(query)
                    overview[metric_name] = result[0]['count'] if result else 0
                except Exception as e:
                    logger.warning(f"Could not get {metric_name}: {e}")
                    overview[metric_name] = 0
            
            return json.dumps({
                "status": "success",
                "company": "Test AI Company",
                "overview": overview,
                "message": "Test AI Company business overview retrieved successfully"
            })
            
        except Exception as e:
            logger.error(f"Failed to get Test AI Company overview: {e}")
            return json.dumps({
                "status": "error",
                "company": "Test AI Company",
                "error": str(e),
                "message": "Failed to get Test AI Company overview"
            })

    @method_tool
    def analyze_test_ai_company_performance(self) -> str:
        """Analyze business performance for Test AI Company."""
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
            performance = results[0] if results else {}

            return json.dumps({
                "status": "success",
                "company": "Test AI Company",
                "performance_metrics": {
                    "total_invoices": performance.get('total_invoices', 0),
                    "total_revenue": float(performance.get('total_revenue', 0)) if performance.get('total_revenue') else 0,
                    "avg_invoice_value": float(performance.get('avg_invoice_value', 0)) if performance.get('avg_invoice_value') else 0
                },
                "period": "Last 30 days",
                "message": "Test AI Company performance analysis completed successfully"
            }, default=str)

        except Exception as e:
            logger.error(f"Failed to analyze Test AI Company performance: {e}")
            return json.dumps({
                "status": "error",
                "company": "Test AI Company",
                "error": str(e),
                "message": "Failed to analyze Test AI Company performance"
            })

    @method_tool
    def search_test_ai_company_knowledge(self, query: str, limit: int = 10) -> str:
        """Search Test AI Company company knowledge base for information."""
        try:
            results = self.knowledge_service.search_knowledge(query, limit=limit)

            if not results:
                return json.dumps({
                    "status": "success",
                    "company": "Test AI Company",
                    "results": [],
                    "count": 0,
                    "message": f"No knowledge base results found for query: {query}"
                })

            # Format results for better readability
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get('title', 'Untitled'),
                    "content": result.get('content', '')[:500] + ('...' if len(result.get('content', '')) > 500 else ''),
                    "type": result.get('type', 'unknown'),
                    "category": result.get('category', 'General')
                })

            return json.dumps({
                "status": "success",
                "company": "Test AI Company",
                "results": formatted_results,
                "count": len(results),
                "message": f"Found {len(results)} knowledge base results for: {query}"
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to search Test AI Company knowledge: {e}")
            return json.dumps({
                "status": "error",
                "company": "Test AI Company",
                "error": str(e),
                "message": f"Failed to search Test AI Company knowledge base"
            })

    @method_tool
    def get_test_ai_company_company_info(self) -> str:
        """Get comprehensive information about Test AI Company company."""
        try:
            # Search for company information in knowledge base
            company_queries = [
                "عن Test AI Company",
                "من هي Test AI Company",
                "about Test AI Company",
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
                return json.dumps({
                    "status": "success",
                    "company": "Test AI Company",
                    "info": [],
                    "message": "No company information found in knowledge base"
                })

            # Format company information
            company_info = []
            for result in unique_results:
                company_info.append({
                    "title": result.get('title', 'Company Information'),
                    "content": result.get('content', ''),
                    "type": result.get('type', 'info')
                })

            return json.dumps({
                "status": "success",
                "company": "Test AI Company",
                "info": company_info,
                "count": len(company_info),
                "message": f"Retrieved comprehensive Test AI Company company information"
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to get Test AI Company company info: {e}")
            return json.dumps({
                "status": "error",
                "company": "Test AI Company",
                "error": str(e),
                "message": f"Failed to retrieve Test AI Company company information"
            })
