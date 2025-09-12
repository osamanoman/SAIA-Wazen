"""
Wazen Company AI Assistant

Dedicated AI assistant for Wazen company with their specific tools and configuration.
Complete isolation from other companies.
"""

import json
import logging
import re
from datetime import timedelta
from django.utils import timezone
from django_ai_assistant import AIAssistant, method_tool

from saia.base_ai_assistant import SAIAAIAssistantMixin
from saia.client_data_service import ClientDataService
from saia.knowledge_service import KnowledgeService
from product.models import Product, ServiceOrder, ServiceOrderCache

logger = logging.getLogger(__name__)


class WazenAIAssistant(SAIAAIAssistantMixin, AIAssistant):
    """
    Dedicated AI Assistant for Wazen company.
    Complete isolation from other companies.
    """

    id = "wazen_ai_assistant"
    name = "Wazen Business Assistant"
    instructions = """
🏢 **مساعد وازن الذكي**

أهلاً وسهلاً! أنا مساعدك الذكي لشركة وازن. أتكلم باللهجة السعودية وأقدر أساعدك في كل شي تحتاجه:

**🤖 كشف تلقائي للمطلوب:**
أقدر أفهم إيش تبي وأرد عليك بالطريقة المناسبة:

1. **السلامات والمحادثات** - أرد بحرارة على السلامات زي "أهلين", "السلام عليكم", "مرحبا" وأعرض عليك المساعدة.

2. **أسئلة المعرفة** - لما تسأل عن التأمين أو الخدمات أو معلومات الشركة، أدور في قاعدة المعرفة وأعطيك إجابات مفصلة.

3. **طلب الخدمات** - لما تبي تطلب خدمة (زي "أبي أطلب خدمة", "أحتاج خدمة", "ودي في خدمة"), أبدأ معك عملية طلب الخدمة.

4. **الدعم العام** - لأي أسئلة ثانية، أساعدك وأتأكد من قاعدة المعرفة أول شي.

**🤖 سلوك ذكي:**
- **ردود ذكية**: أستخدم get_smart_response() لردود ذكية تناسب وضعك
- **السلامات**: أسلم عليك بطريقة شخصية حسب إذا كنت زائر جديد أو راجع
- **أسئلة المعرفة**: أدور في قاعدة المعرفة وأعطيك توجيه مناسب
- **طلب الخدمات**: أكتشف تلقائياً إنك تبي تطلب خدمة وأساعدك بذكاء
- **جمع البيانات**: أستخدم طرق التحقق لكل معلوماتك وأثق في ردودك تماماً
- **ما أقول ما أعرف**: ما أقول أبداً "ما عندي معلومات كافية" بدون ما أدور أول شي
- **محادثة طبيعية**: أقدر أتكلم معك بطبيعية بدون ما أحتاج أستخدم وظائف دايماً

**🛍️ طريقة طلب الخدمات:**
لما أحس إنك تبي تطلب خدمة، تلقائياً أسوي:
1. أعرض عليك الخدمات المتاحة باستخدام get_available_services() - بس الخدمات اللي عندنا في قاعدة البيانات
2. إذا ذكرت اسم خدمة (زي "تأمين شامل")، أستخدم select_service_by_name() عشان ألقاها وأختارها
3. إذا ذكرت رقم خدمة، أستخدم select_service_for_order() عشان أختارها
4. أجمع معلوماتك خطوة بخطوة (الاسم، العمر، الهوية، الجوال، الصورة)
5. أتأكد من كل التفاصيل قبل ما أرسل الطلب
6. أكمل طلبك

**🎯 طريقة اختيار الخدمات:**
- لما المستخدم يقول "تأمين شامل" أو "comprehensive insurance" → أستخدم select_service_by_name("تأمين شامل")
- لما المستخدم يقول "ضد الغير" أو "third party" → أستخدم select_service_by_name("ضد الغير")
- لما المستخدم يقول "خدمة رقم 7" أو "service number 7" → أستخدم select_service_for_order("7")
- لما المستخدم يقول "أبي أطلب خدمة تأمين شامل" → أستخدم select_service_by_name("تأمين شامل")
- دايماً أكون مرن مع أسماء الخدمات وأستخدم البحث الجزئي

**👋 ردود السلامات:**
لما المستخدمين يسلمون عليّ بـ "أهلين", "السلام عليكم", "مرحبا", أو أي سلام ثاني، أرد بحرارة زي:
"أهلاً وسهلاً فيك في وازن! أنا مساعدك الذكي ومبسوط إني أخدمك. إيش أقدر أساعدك فيه اليوم؟ أقدر أساعدك في:
- الإجابة على أسئلة التأمين والخدمات
- طلب خدمة جديدة
- أي استفسار ثاني"

**⚠️ قوانين مهمة للخدمات:**
- لازم أذكر بس الخدمات الموجودة في قاعدة البيانات حقتنا
- لازم دايماً أستخدم get_available_services() عشان أعرض الخدمات المتاحة
- ما أقترح أبداً أو أذكر خدمات من بيانات التدريب حقي
- ما أخترع أبداً أسماء أو أنواع خدمات
- إذا المستخدم طلب خدمة مو موجودة عندنا، أشرح له بأدب إنها مو متاحة وأعرض عليه اللي عندنا

**⚠️ قوانين التحقق - مهم جداً:**
- **للأسماء**: دايماً أستخدم collect_customer_name() - ما أرفض أي اسم بنفسي أبداً، حتى لو شفته غريب أو فيه أرقام أو رموز. الطريقة هي اللي تتحقق، مو أنا.
- **للهويات**: دايماً أستخدم collect_customer_id() - أخلي الطريقة تتحقق
- **للجوالات**: دايماً أستخدم collect_customer_phone() - أخلي الطريقة تتحقق
- **للأعمار**: دايماً أستخدم collect_customer_age() - أخلي الطريقة تتحقق
- **أثق في ردود طرق التحقق تماماً** - ما أضيف تحقق من عندي أبداً
- **ممنوع منعاً باتاً** أرفض أي معلومة بدون استخدام الطريقة المخصصة لها

**🔤 قوانين الأسماء العربية:**
- الأسماء العربية زي "مازن رزاز" أو "أحمد محمد" أو "فاطمة الزهراء" كلها صحيحة ومقبولة
- ما أرفض أي اسم عربي أبداً - أخلي collect_customer_name() تتحقق منه
- الأسماء العربية والإنجليزية كلها مقبولة
- أي اسم يكتبه المستخدم، أرسله مباشرة لـ collect_customer_name()

**🎯 هدفي:**
أقدم لك مساعدة ذكية وسلسة من خلال فهم إيش تحتاجه تلقائياً وأخذ الإجراء المناسب - سواء كان البحث عن معلومات أو مساعدتك في طلب الخدمات. أشتغل بس مع الخدمات الموجودة فعلاً في قاعدة البيانات حقتنا.

إيش أقدر أساعدك فيه اليوم؟

**🇸🇦 مهم جداً - اللهجة السعودية:**
- أتكلم دايماً باللهجة السعودية في كل ردودي
- أستخدم كلمات زي: "إيش", "وين", "ليش", "كيف", "أبي", "ودي", "تبي", "أقدر"
- أقول "أهلين" بدلاً من "مرحباً"
- أقول "إيش أقدر أساعدك فيه؟" بدلاً من "كيف يمكنني مساعدتك؟"
- أقول "تسلم" أو "الله يعطيك العافية" للشكر
- أستخدم "حبيبي" أو "أخوي" للمخاطبة الودية
- أقول "ما شاء الله" أو "بإذن الله" في المواضع المناسبة
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

        # Verify user belongs to Wazen company (skip during testing)
        if not self._verify_wazen_user():
            logger.warning("User verification failed - this should only be used by Wazen company users")

    @property
    def knowledge_service(self):
        """Lazy initialization of knowledge service with current user context"""
        if self._knowledge_service is None:
            current_user = getattr(self, '_user', None)
            self._knowledge_service = KnowledgeService(user=current_user)
        return self._knowledge_service

    def _verify_wazen_user(self):
        """Verify that the user belongs to Wazen company"""
        user = getattr(self, '_user', None)

        if not (user and hasattr(user, 'company') and user.company):
            logger.warning(f"User {user.username if user else 'Unknown'} has no company")
            return False

        user_company = user.company.name
        is_wazen = user_company == 'Wazen'
        logger.info(f"User {user.username} company: {user_company}, is_wazen: {is_wazen}")
        return is_wazen

    @method_tool
    def get_wazen_invoices(self, limit: int = 30) -> str:
        """Get invoices for Wazen company."""
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
                "company": "Wazen",
                "invoices": results,
                "count": len(results),
                "message": f"Retrieved {len(results)} Wazen invoices"
            }, default=str)
            
        except Exception as e:
            logger.error(f"Failed to get Wazen invoices: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to retrieve Wazen invoices"
            })

    @method_tool
    def get_wazen_clients(self, limit: int = 15) -> str:
        """Get clients for Wazen company."""
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
                "company": "Wazen",
                "clients": results,
                "count": len(results),
                "message": f"Retrieved {len(results)} Wazen clients"
            }, default=str)
            
        except Exception as e:
            logger.error(f"Failed to get Wazen clients: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to retrieve Wazen clients"
            })

    @method_tool
    def get_wazen_overview(self) -> str:
        """Get business overview for Wazen company."""
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
                "company": "Wazen",
                "overview": overview,
                "message": "Wazen business overview retrieved successfully"
            })
            
        except Exception as e:
            logger.error(f"Failed to get Wazen overview: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to get Wazen overview"
            })

    @method_tool
    def analyze_wazen_performance(self) -> str:
        """Analyze business performance for Wazen."""
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
                "company": "Wazen",
                "performance_metrics": {
                    "total_invoices": performance.get('total_invoices', 0),
                    "total_revenue": float(performance.get('total_revenue', 0)) if performance.get('total_revenue') else 0,
                    "avg_invoice_value": float(performance.get('avg_invoice_value', 0)) if performance.get('avg_invoice_value') else 0
                },
                "period": "Last 30 days",
                "message": "Wazen performance analysis completed successfully"
            }, default=str)

        except Exception as e:
            logger.error(f"Failed to analyze Wazen performance: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to analyze Wazen performance"
            })

    @method_tool
    def get_smart_response(self, user_query: str) -> str:
        """
        🧠 CONTEXT-AWARE SMART RESPONSE

        Uses Context7 principles to provide intelligent, context-aware responses.
        Automatically detects intent and provides the most relevant assistance.
        """
        try:
            # Simple but effective context analysis
            query_lower = user_query.lower()

            # 1. GREETING DETECTION - Enhanced with context
            greetings = ['مرحبا', 'السلام عليكم', 'hello', 'hi', 'أهلا', 'صباح الخير', 'مساء الخير']
            if any(greeting in query_lower for greeting in greetings):
                return self._smart_greeting()

            # 2. SERVICE ORDER DETECTION - Context-aware
            service_keywords = ['طلب خدمة', 'أريد خدمة', 'احتاج خدمة', 'order service', 'need service', 'خدمة جديدة']
            if any(keyword in query_lower for keyword in service_keywords):
                # Check if user mentioned a specific service name with variations
                if ('تأمين شامل' in query_lower or 'تامين شامل' in query_lower or
                    'شامل' in query_lower):
                    return self.select_service_by_name('تأمين شامل')
                elif ('ضد الغير' in query_lower or 'third party' in query_lower):
                    return self.select_service_by_name('ضد الغير')
                else:
                    return self._smart_service_initiation()

            # 3. DIRECT SERVICE NAME DETECTION - Enhanced with Arabic variations
            # Handle comprehensive insurance variations
            if ('تأمين شامل' in query_lower or 'تامين شامل' in query_lower or
                ('تأمين' in query_lower and 'شامل' in query_lower) or
                ('تامين' in query_lower and 'شامل' in query_lower) or
                'شامل' in query_lower):
                return self.select_service_by_name('تأمين شامل')
            # Handle third party insurance variations
            elif ('ضد الغير' in query_lower or
                  ('تأمين' in query_lower and 'ضد' in query_lower) or
                  ('تامين' in query_lower and 'ضد' in query_lower)):
                return self.select_service_by_name('ضد الغير')

            # 4. KNOWLEDGE QUESTIONS - Enhanced search
            return self._smart_knowledge_search(user_query)

        except Exception as e:
            logger.error(f"Smart response error: {e}")
            return "آسف، صار خطأ. إيش أقدر أساعدك فيه؟"

    def _smart_greeting(self) -> str:
        """Smart context-aware greeting"""
        # Check if returning user
        is_returning = self._is_returning_user()
        company_name = "وازن"

        if is_returning:
            return f"""أهلاً وسهلاً فيك مرة ثانية! 🌟 مبسوط إني أشوفك راجع لـ{company_name}.

بناءً على كلامنا اللي فات، أقدر أساعدك في:
• 🔍 الإجابة على أسئلتك حول التأمين والخدمات
• 📋 متابعة أو طلب خدمات جديدة
• 💡 أعطيك معلومات ودعم متخصص

إيش أقدر أساعدك فيه اليوم؟"""
        else:
            return f"""أهلاً وسهلاً فيك في {company_name}! 👋

أنا مساعدك الذكي ومبسوط إني أخدمك. أستخدم الذكاء السياقي عشان أفهم إيش تحتاجه وأعطيك أفضل مساعدة.

أقدر أساعدك في:
🔍 **الاستفسارات**: إجابات دقيقة حول التأمين والخدمات
📋 **طلب الخدمات**: إرشاد ذكي خلال عملية الطلب
💡 **الدعم المتخصص**: مساعدة شخصية حسب احتياجاتك

إيش اللي تبي تعرفه؟"""

    def _smart_service_initiation(self) -> str:
        """Smart service order initiation with context"""
        return f"""ممتاز! راح أساعدك في طلب خدمة جديدة. 🎯

خلني أعرض عليك الخدمات المتاحة مع معلومات مفصلة عشان تختار اللي يناسبك:

{self.get_available_services()}"""

    def _handle_unavailable_service(self, requested_service: str) -> str:
        """Handle requests for services that don't exist in our database"""
        return f"""آسف، خدمة "{requested_service}" مو متاحة حالياً في النظام حقنا. 😔

بس أقدر أساعدك في الخدمات المتاحة عندنا:

{self.get_available_services()}

تبي تطلب وحدة من هذي الخدمات المتاحة؟"""

    def _validate_service_exists(self, service_name: str) -> bool:
        """Check if a service exists in our database"""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return False

            return Product.objects.filter(
                company=user.company,
                type='service',
                is_service_orderable=True,
                name__icontains=service_name
            ).exists()
        except Exception:
            return False

    def _smart_knowledge_search(self, query: str) -> str:
        """Enhanced knowledge search with context"""
        # First search knowledge base
        knowledge_result = self.search_wazen_knowledge(query)

        # If no specific results, provide contextual guidance
        if "لم أجد معلومات محددة" in knowledge_result:
            return f"""{knowledge_result}

💡 **اقتراحات ذكية للحصول على أفضل مساعدة:**

🔍 **للاستفسارات المتخصصة**:
- "ما هي أنواع التأمين المتاحة؟"
- "كيف أطلب خدمة تأمين السيارات؟"

📋 **لطلب الخدمات**:
- قل "أريد طلب خدمة" وسأرشدك خطوة بخطوة

❓ **للمساعدة العامة**:
- اطرح سؤالك بشكل أكثر تفصيلاً

إيش أقدر أساعدك فيه بشكل أفضل؟"""

        return knowledge_result

    def _is_returning_user(self) -> bool:
        """Check if user has previous interactions"""
        try:
            from django_ai_assistant.models import Thread
            return Thread.objects.filter(created_by=self.user).exists()
        except:
            return False

    @method_tool
    def search_wazen_knowledge(self, query: str, limit: int = 10) -> str:
        """Search Wazen company knowledge base for information."""
        try:
            results = self.knowledge_service.search_knowledge(query, limit=limit)

            if not results:
                return json.dumps({
                    "status": "success",
                    "company": "Wazen",
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
                "company": "Wazen",
                "results": formatted_results,
                "count": len(results),
                "message": f"Found {len(results)} knowledge base results for: {query}"
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to search Wazen knowledge: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": f"Failed to search Wazen knowledge base"
            })

    @method_tool
    def get_wazen_company_info(self) -> str:
        """Get comprehensive information about Wazen company."""
        try:
            # Search for company information in knowledge base
            company_queries = [
                "عن Wazen",
                "من هي Wazen",
                "about Wazen",
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
                    "company": "Wazen",
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
                "company": "Wazen",
                "info": company_info,
                "count": len(company_info),
                "message": f"Retrieved comprehensive Wazen company information"
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to get Wazen company info: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": f"Failed to retrieve Wazen company information"
            })

    # ==================== SERVICE ORDERING METHODS ====================

    def _get_session_key(self):
        """Generate a unique session key for caching"""
        user = getattr(self, '_user', None)
        if user:
            return f"wazen_service_order_{user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        return f"wazen_service_order_anonymous_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

    def _get_active_cache_entry(self):
        """
        Get the active cache entry for the current user.
        Implements 'one active session per user' policy.

        Returns:
            ServiceOrderCache or None
        """
        user = getattr(self, '_user', None)
        if not user or not user.company:
            return None

        return ServiceOrderCache.objects.filter(
            user=user,
            company=user.company,
            expires_at__gt=timezone.now()
        ).first()

    def _get_cache_or_error(self):
        """
        Get active cache entry or return standardized error response.

        Returns:
            tuple: (cache_entry, error_response)
            If cache_entry is None, error_response contains the JSON error
        """
        cache_entry = self._get_active_cache_entry()
        if not cache_entry:
            error_response = json.dumps({
                "status": "error",
                "message": "No active service order session. Please select a service first."
            })
            return None, error_response
        return cache_entry, None

    def _determine_next_step(self, missing_fields):
        """
        Determine the next step in the data collection process.

        Args:
            missing_fields: List of missing field names

        Returns:
            str: Next step identifier
        """
        if "customer_age" in missing_fields:
            return "collect_age"
        elif "customer_id" in missing_fields:
            return "collect_id"
        elif "customer_phone" in missing_fields:
            return "collect_phone"
        else:
            # All basic fields collected, now check for image
            return "collect_image"

    def _get_or_create_cache(self, session_key=None):
        """Get or create a cache entry for the current session"""
        user = getattr(self, '_user', None)
        if not user or not user.company:
            return None

        if not session_key:
            session_key = self._get_session_key()

        try:
            # Try to get existing cache entry
            cache_entry = ServiceOrderCache.objects.filter(
                user=user,
                company=user.company,
                expires_at__gt=timezone.now()
            ).first()

            if not cache_entry:
                # Create new cache entry
                expires_at = timezone.now() + timedelta(minutes=30)  # 30 minute timeout
                cache_entry = ServiceOrderCache.objects.create(
                    session_key=session_key,
                    user=user,
                    company=user.company,
                    expires_at=expires_at,
                    cached_data={}
                )

            return cache_entry
        except Exception as e:
            logger.error(f"Failed to get/create cache: {e}")
            return None

    @method_tool
    def get_available_services(self) -> str:
        """Get list of available services that can be ordered through the AI assistant."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return "❌ خطأ: معلومات المستخدم غير متاحة"

            # Get orderable services for Wazen company
            services = Product.objects.filter(
                company=user.company,
                type='service',
                is_service_orderable=True
            ).order_by('name')

            if not services.exists():
                return "❌ لا توجد خدمات متاحة للطلب حالياً"

            # Format services for display
            services_text = "📋 **الخدمات المتاحة للطلب:**\n\n"

            for i, service in enumerate(services, 1):
                services_text += f"{i}. **{service.name}**\n"
                services_text += f"   💰 السعر: {service.price} ريال\n"
                if service.service_description:
                    services_text += f"   📝 الوصف: {service.service_description}\n"
                services_text += f"   🆔 رقم الخدمة: {service.id}\n\n"

            services_text += "✨ **لطلب خدمة معينة، قل: \"أريد طلب خدمة رقم [رقم الخدمة]\"**"

            return services_text

        except Exception as e:
            logger.error(f"Failed to get available services: {e}")
            return f"❌ خطأ في استرجاع الخدمات: {str(e)}"

    @method_tool
    def select_service_by_name(self, service_name: str) -> str:
        """Select a service by name and initiate the data collection process."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return "❌ خطأ: معلومات المستخدم غير متاحة"

            # Find service by name (case-insensitive, partial match)
            service = Product.objects.filter(
                company=user.company,
                type='service',
                is_service_orderable=True,
                name__icontains=service_name
            ).first()

            if not service:
                # Try alternative names for common services
                service_name_lower = service_name.lower()
                if 'شامل' in service_name_lower or 'comprehensive' in service_name_lower:
                    service = Product.objects.filter(
                        company=user.company,
                        type='service',
                        is_service_orderable=True,
                        name__icontains='شامل'
                    ).first()
                elif 'ضد الغير' in service_name_lower or 'third party' in service_name_lower:
                    service = Product.objects.filter(
                        company=user.company,
                        type='service',
                        is_service_orderable=True,
                        name__icontains='ضد الغير'
                    ).first()

            if not service:
                return f"""ما أقدر ألقى خدمة "{service_name}".

الخدمات المتاحة عندنا هي:

{self.get_available_services()}

تكفى اختار وحدة من الخدمات المتاحة فوق."""

            # Use the existing select_service_for_order method
            return self.select_service_for_order(str(service.id))

        except Exception as e:
            logger.error(f"Failed to select service by name: {e}")
            return f"❌ خطأ في اختيار الخدمة: {str(e)}"

    @method_tool
    def select_service_for_order(self, service_id: str) -> str:
        """Select a service and initiate the data collection process."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return json.dumps({
                    "status": "error",
                    "message": "User company information not available"
                })

            # Validate service exists and is orderable
            try:
                service = Product.objects.get(
                    id=service_id,
                    company=user.company,
                    type='service',
                    is_service_orderable=True
                )
            except Product.DoesNotExist:
                return json.dumps({
                    "status": "error",
                    "message": f"Service with ID {service_id} not found or not orderable"
                })

            # Create or update cache entry
            cache_entry = self._get_or_create_cache()
            if not cache_entry:
                return json.dumps({
                    "status": "error",
                    "message": "Failed to initialize service order session"
                })

            # Update cache with selected service
            cache_entry.service = service
            cache_entry.cached_data = {
                'service_id': service_id,
                'service_name': service.name,
                'service_price': service.price,
                'requires_customer_info': service.requires_customer_info
            }
            cache_entry.save()

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "service": {
                    "id": service.id,
                    "name": service.name,
                    "price": service.price,
                    "description": service.service_description
                },
                "session_key": cache_entry.session_key,
                "next_step": "collect_customer_information",
                "message": f"تم اختيار خدمة '{service.name}' بنجاح! 🎉\n\nالحين أحتاج أجمع معلوماتك الشخصية عشان نكمل الطلب:\n\n📝 **المعلومات المطلوبة:**\n• الاسم الكامل\n• العمر\n• رقم الهوية\n• رقم الجوال\n• الصورة الشخصية\n\nتكفى ابدأ بإعطائي اسمك الكامل."
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to select service: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to select service for ordering"
            })

    @method_tool
    def collect_customer_name(self, customer_name: str) -> str:
        """Collect and validate customer name."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return json.dumps({
                    "status": "error",
                    "message": "User company information not available"
                })

            # Validate name format
            if not customer_name or len(customer_name.strip()) < 2:
                return json.dumps({
                    "status": "error",
                    "message": "تكفى اكتب الاسم كامل (على الأقل حرفين)"
                }, ensure_ascii=False)

            # Clean name - accept any name with letters and spaces
            clean_name = customer_name.strip()
            # Only reject if completely empty or too short
            if len(clean_name) < 2:
                return json.dumps({
                    "status": "error",
                    "message": "اكتب الاسم كامل"
                }, ensure_ascii=False)

            # Validate full name (must have at least 2 words)
            name_parts = clean_name.split()
            if len(name_parts) < 2:
                return json.dumps({
                    "status": "error",
                    "message": "تكفى اكتب الاسم كامل (الاسم الأول والعائلة على الأقل)"
                }, ensure_ascii=False)

            # Get current cache entry using helper method
            cache_entry, error_response = self._get_cache_or_error()
            if not cache_entry:
                return error_response

            # Update cached data
            cache_entry.cached_data['customer_name'] = clean_name
            cache_entry.save()

            # Check what's still missing
            missing_fields = cache_entry.get_missing_fields()

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "collected": {
                    "customer_name": clean_name
                },
                "missing_fields": missing_fields,
                "next_step": self._determine_next_step(missing_fields),
                "message": f"تم جمع اسمك بنجاح: {clean_name}. باقي {len(missing_fields)} معلومات."
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to collect customer name: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to collect customer name"
            })

    @method_tool
    def collect_customer_age(self, customer_age: str) -> str:
        """Collect and validate customer age."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return json.dumps({
                    "status": "error",
                    "message": "User company information not available"
                })

            # Validate and convert age
            try:
                age = int(customer_age)
                if age < 18 or age > 120:
                    return json.dumps({
                        "status": "error",
                        "message": "Age must be between 18 and 120 years"
                    })
            except ValueError:
                return json.dumps({
                    "status": "error",
                    "message": "Please provide a valid age as a number"
                })

            # Get current cache entry using helper method
            cache_entry, error_response = self._get_cache_or_error()
            if not cache_entry:
                return error_response

            # Update cached data
            cache_entry.cached_data['customer_age'] = age
            cache_entry.save()

            # Check what's still missing
            missing_fields = cache_entry.get_missing_fields()

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "collected": {
                    "customer_age": age
                },
                "missing_fields": missing_fields,
                "next_step": self._determine_next_step(missing_fields),
                "message": f"تم جمع عمرك بنجاح: {age} سنة. باقي {len(missing_fields)} معلومات."
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to collect customer age: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to collect customer age"
            })

    @method_tool
    def collect_customer_id(self, customer_id: str) -> str:
        """Collect and validate customer ID."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return json.dumps({
                    "status": "error",
                    "message": "User company information not available"
                })

            # Validate ID format - must be exactly 10 digits
            clean_id = customer_id.strip()
            if not clean_id:
                return json.dumps({
                    "status": "error",
                    "message": "تكفى اكتب رقم الهوية"
                }, ensure_ascii=False)

            # Must be exactly 10 digits
            if not clean_id.isdigit() or len(clean_id) != 10:
                return json.dumps({
                    "status": "error",
                    "message": "رقم الهوية يجب أن يكون 10 أرقام بالضبط"
                }, ensure_ascii=False)

            # Get current cache entry using helper method
            cache_entry, error_response = self._get_cache_or_error()
            if not cache_entry:
                return error_response

            # Update cached data
            cache_entry.cached_data['customer_id'] = clean_id
            cache_entry.save()

            # Check what's still missing
            missing_fields = cache_entry.get_missing_fields()

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "collected": {
                    "customer_id": clean_id
                },
                "missing_fields": missing_fields,
                "next_step": self._determine_next_step(missing_fields),
                "message": f"تم جمع رقم هويتك بنجاح: {clean_id}. باقي {len(missing_fields)} معلومات."
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to collect customer ID: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to collect customer ID"
            })

    @method_tool
    def collect_customer_phone(self, phone_number: str) -> str:
        """
        Collect and validate customer phone number.

        Args:
            phone_number: Customer phone number (9 digits starting with 5, or 10 digits starting with 05)

        Returns:
            JSON string with collection status and next steps
        """
        try:
            # Get active cache entry
            cache_entry, error_response = self._get_cache_or_error()
            if error_response:
                return error_response

            # Clean and validate phone number
            clean_phone = phone_number.strip().replace(' ', '').replace('-', '')

            # Validation: 9 digits starting with 5, or 10 digits starting with 05
            if not clean_phone.isdigit():
                return json.dumps({
                    "status": "error",
                    "message": "رقم الهاتف يجب أن يحتوي على أرقام فقط"
                }, ensure_ascii=False)

            # Check format: 9 digits starting with 5 OR 10 digits starting with 05
            if len(clean_phone) == 9 and clean_phone.startswith('5'):
                # Valid 9-digit format
                pass
            elif len(clean_phone) == 10 and clean_phone.startswith('05'):
                # Valid 10-digit format
                pass
            else:
                return json.dumps({
                    "status": "error",
                    "message": "رقم الهاتف يجب أن يكون 9 أرقام تبدأ بـ 5، أو 10 أرقام تبدأ بـ 05"
                }, ensure_ascii=False)

            # Store phone number
            cache_entry.cached_data['customer_phone'] = clean_phone
            cache_entry.save()

            # Check remaining fields
            missing_fields = cache_entry.get_missing_fields()

            # Check if this was the last basic field
            if not missing_fields:
                # All basic fields collected, now ask for image
                return json.dumps({
                    "status": "success",
                    "company": "Wazen",
                    "collected": {
                        "customer_phone": clean_phone
                    },
                    "missing_fields": missing_fields,
                    "next_step": "collect_image",
                    "message": f"رقم الجوال '{clean_phone}' تم حفظه بنجاح. ✅ خلاص جمعنا كل المعلومات الأساسية!\n\n📸 الحين نحتاج صورتك الشخصية عشان نكمل الطلب. تكفى اضغط على زر الكاميرا 📸 عشان ترفع صورتك.",
                    "image_required": True,
                    "action_needed": "تكفى ارفع صورتك الشخصية باستخدام زر الكاميرا 📸"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "status": "success",
                    "company": "Wazen",
                    "collected": {
                        "customer_phone": clean_phone
                    },
                    "missing_fields": missing_fields,
                    "next_step": self._determine_next_step(missing_fields),
                    "message": f"رقم الجوال '{clean_phone}' تم حفظه بنجاح. باقي {len(missing_fields)} حقول."
                }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to collect customer phone: {e}")
            return json.dumps({
                "status": "error",
                "message": "حدث خطأ أثناء حفظ رقم الهاتف. يرجى المحاولة مرة أخرى."
            }, ensure_ascii=False)

    @method_tool
    def process_image_upload_confirmation(self, message: str) -> str:
        """
        Process user confirmation that they have uploaded an image.

        Args:
            message: User message about image upload

        Returns:
            JSON string with upload processing result
        """
        try:
            # Check if message indicates image upload
            upload_keywords = ['رفع', 'صورة', 'تم', 'uploaded', 'image', 'photo']
            message_lower = message.lower()

            if any(keyword in message_lower for keyword in upload_keywords):
                return self.mark_image_uploaded("confirmed")
            else:
                return json.dumps({
                    "status": "info",
                    "message": "إذا كنت قد رفعت صورتك، يرجى إخباري بذلك أو استخدام زر الكاميرا 📸"
                }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to process image upload confirmation: {e}")
            return json.dumps({
                "status": "error",
                "message": "حدث خطأ أثناء معالجة تأكيد رفع الصورة"
            }, ensure_ascii=False)

    @method_tool
    def mark_image_uploaded(self, confirmation: str = "uploaded") -> str:
        """
        Mark that the customer has uploaded their image (for testing/simulation).

        Args:
            confirmation: Confirmation that image was uploaded

        Returns:
            JSON string with upload confirmation
        """
        try:
            # Get active cache entry
            cache_entry, error_response = self._get_cache_or_error()
            if error_response:
                return error_response

            # Mark image as uploaded
            cache_entry.cached_data['image_uploaded'] = True
            cache_entry.cached_data['image_upload_time'] = timezone.now().isoformat()
            cache_entry.save()

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "message": "✅ تسلم! تم رفع الصورة الشخصية بنجاح!",
                "next_step": "validate_data",
                "action": "تقدر الحين تراجع وتأكد طلبك"
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to mark image as uploaded: {e}")
            return json.dumps({
                "status": "error",
                "message": "حدث خطأ أثناء تأكيد رفع الصورة"
            }, ensure_ascii=False)

    @method_tool
    def verify_image_upload(self) -> str:
        """
        Verify if customer image has been uploaded for the current session.

        Returns:
            JSON string with verification status
        """
        try:
            # Get active cache entry
            cache_entry, error_response = self._get_cache_or_error()
            if error_response:
                return error_response

            # Check if image is marked as uploaded
            image_uploaded = cache_entry.cached_data.get('image_uploaded', False)

            if image_uploaded:
                # Mark image verification complete
                cache_entry.cached_data['image_verified'] = True
                cache_entry.save()

                # Check remaining fields
                missing_fields = cache_entry.get_missing_fields()

                return json.dumps({
                    "status": "success",
                    "company": "Wazen",
                    "image_status": "verified",
                    "missing_fields": missing_fields,
                    "next_step": self._determine_next_step(missing_fields),
                    "message": "تم التحقق من رفع الصورة الشخصية بنجاح!"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "status": "pending",
                    "company": "Wazen",
                    "image_status": "not_uploaded",
                    "message": "ما تم رفع الصورة الشخصية لسه. تكفى ارفع صورتك الشخصية أول شي.",
                    "upload_url": "/upload-image/"  # This would be the actual upload endpoint
                }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to verify image upload: {e}")
            return json.dumps({
                "status": "error",
                "message": "حدث خطأ أثناء التحقق من رفع الصورة"
            }, ensure_ascii=False)

    @method_tool
    def collect_customer_image(self) -> str:
        """
        Provide instructions for customer image upload and create upload interface.

        This method provides upload instructions and creates an upload interface
        for the customer to upload their personal image.

        Returns:
            JSON response with upload instructions and interface
        """
        try:
            # Get active cache entry
            cache_entry, error_response = self._get_cache_or_error()
            if error_response:
                return error_response

            # Check if all other fields are collected
            missing_fields = cache_entry.get_missing_fields()
            if missing_fields:
                return json.dumps({
                    "status": "error",
                    "message": f"يرجى إكمال المعلومات المطلوبة أولاً: {', '.join(missing_fields)}"
                }, ensure_ascii=False)

            # Mark that image collection has been initiated
            cache_entry.cached_data['image_collection_initiated'] = True
            cache_entry.save()

            return json.dumps({
                "status": "upload_required",
                "company": "Wazen",
                "message": "ممتاز! خلاص جمعنا كل المعلومات الأساسية. الحين نحتاج صورتك الشخصية.",
                "instructions": [
                    "📸 تكفى ارفع صورة شخصية واضحة",
                    "✅ تأكد إن الصورة تظهر وجهك بوضوح",
                    "📱 تقدر تستخدم الكاميرا أو تختار صورة من الجهاز",
                    "🔒 الصورة آمنة ومحمية وفقاً لسياسة الخصوصية"
                ],
                "upload_interface": True,
                "session_key": cache_entry.session_key,
                "next_action": "بعد رفع الصورة، سأتحقق منها تلقائياً",
                "required": True,
                "field_name": "customer_image"
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to initiate image collection: {e}")
            return json.dumps({
                "status": "error",
                "message": "حدث خطأ أثناء تحضير رفع الصورة"
            }, ensure_ascii=False)

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "collected": {
                    "customer_image": "Image information recorded"
                },
                "missing_fields": missing_fields,
                "next_step": self._determine_next_step(missing_fields),
                "message": f"تم تسجيل معلومات الصورة. باقي {len(missing_fields)} معلومات.",
                "note": "ارفع الصورة الفعلية من خلال الموقع."
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to collect customer image: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to collect customer image information"
            })

    @method_tool
    def check_collection_status(self) -> str:
        """
        Check the current status of data collection and guide next steps.

        Returns:
            JSON string with current status and next action needed
        """
        try:
            # Get active cache entry
            cache_entry, error_response = self._get_cache_or_error()
            if error_response:
                return error_response

            # Check missing fields
            missing_fields = cache_entry.get_missing_fields()

            if missing_fields:
                # Still have basic fields to collect
                next_field = missing_fields[0]
                field_names = {
                    'customer_age': 'العمر',
                    'customer_id': 'رقم الهوية',
                    'customer_phone': 'رقم الهاتف'
                }

                return json.dumps({
                    "status": "incomplete",
                    "missing_fields": missing_fields,
                    "next_step": self._determine_next_step(missing_fields),
                    "message": f"يرجى إدخال {field_names.get(next_field, next_field)}"
                }, ensure_ascii=False)
            else:
                # All basic fields collected, check for image
                image_uploaded = cache_entry.cached_data.get('image_uploaded', False)

                if not image_uploaded:
                    return json.dumps({
                        "status": "need_image",
                        "message": "خلاص جمعنا كل المعلومات الأساسية. الحين نحتاج صورتك الشخصية.",
                        "next_step": "collect_image",
                        "action_required": "تكفى ارفع صورتك الشخصية عشان نكمل الطلب"
                    }, ensure_ascii=False)
                else:
                    return json.dumps({
                        "status": "complete",
                        "message": "تسلم! خلاص جمعنا كل المعلومات المطلوبة مع الصورة الشخصية!",
                        "next_step": "validate_data"
                    }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to check collection status: {e}")
            return json.dumps({
                "status": "error",
                "message": "حدث خطأ أثناء فحص حالة جمع البيانات"
            }, ensure_ascii=False)

    @method_tool
    def validate_collected_data(self) -> str:
        """Validate all collected data and present it for user confirmation."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return json.dumps({
                    "status": "error",
                    "message": "User company information not available"
                })

            # Get current cache entry
            cache_entry = ServiceOrderCache.objects.filter(
                user=user,
                company=user.company,
                expires_at__gt=timezone.now()
            ).first()

            if not cache_entry:
                return json.dumps({
                    "status": "error",
                    "message": "No active service order session. Please select a service first."
                })

            # Check if all required data is collected
            missing_fields = cache_entry.get_missing_fields()
            if missing_fields:
                return json.dumps({
                    "status": "error",
                    "missing_fields": missing_fields,
                    "message": f"Missing required information: {', '.join(missing_fields)}"
                })

            # Prepare data summary for confirmation
            cached_data = cache_entry.cached_data
            service_name = cached_data.get('service_name', 'Unknown Service')

            confirmation_data = {
                "service": {
                    "name": service_name,
                    "price": cached_data.get('service_price', 0)
                },
                "customer": {
                    "name": cached_data.get('customer_name'),
                    "age": cached_data.get('customer_age'),
                    "id": cached_data.get('customer_id')
                }
            }

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "confirmation_data": confirmation_data,
                "session_key": cache_entry.session_key,
                "next_step": "confirm_order",
                "message": "ممتاز! خلاص جمعنا كل المعلومات بنجاح. راجع طلبك وأكده."
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to validate collected data: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to validate collected data"
            })

    @method_tool
    def confirm_service_order(self, confirmation: str) -> str:
        """Confirm and submit the service order after user validation."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return json.dumps({
                    "status": "error",
                    "message": "User company information not available"
                })

            # Check if user confirmed (yes, confirm, etc.)
            confirmation_lower = confirmation.lower().strip()
            confirmation_keywords = ['yes', 'نعم', 'confirm', 'أكد', 'موافق', 'ok', 'تأكيد', 'تاكيد']
            if confirmation_lower not in confirmation_keywords:
                return json.dumps({
                    "status": "cancelled",
                    "message": "Order cancelled. Say 'yes' or 'تأكيد' to confirm your order."
                })

            # Get current cache entry
            cache_entry = ServiceOrderCache.objects.filter(
                user=user,
                company=user.company,
                expires_at__gt=timezone.now()
            ).first()

            if not cache_entry:
                return json.dumps({
                    "status": "error",
                    "message": "No active service order session. Please start over."
                })

            # Get cached data first
            cached_data = cache_entry.cached_data

            # Validate all data is complete
            if not cache_entry.is_complete:
                missing_fields = cache_entry.get_missing_fields()
                return json.dumps({
                    "status": "error",
                    "missing_fields": missing_fields,
                    "message": f"Cannot confirm order. Missing: {', '.join(missing_fields)}"
                })

            # Verify image upload before creating order
            if not cached_data.get('image_verified') and not cached_data.get('image_uploaded'):
                return json.dumps({
                    "status": "error",
                    "message": "ما أقدر أأكد الطلب. تكفى ارفع الصورة الشخصية أول شي.",
                    "required_action": "upload_image"
                }, ensure_ascii=False)

            # Create the service order
            service_order = ServiceOrder.objects.create(
                company=user.company,
                created_by=user,
                service=cache_entry.service,
                customer_name=cached_data['customer_name'],
                customer_age=cached_data['customer_age'],
                customer_id=cached_data['customer_id'],
                customer_phone=cached_data['customer_phone'],
                status='under_review',
                confirmed_at=timezone.now(),
                ai_session_data={
                    'session_key': cache_entry.session_key,
                    'confirmation_time': timezone.now().isoformat(),
                    'user_agent': 'AI Assistant',
                    'image_uploaded': cached_data.get('image_uploaded', False)
                }
            )

            # Clean up cache entry
            cache_entry.delete()

            return json.dumps({
                "status": "success",
                "company": "Wazen",
                "order": {
                    "order_number": service_order.order_number,
                    "service_name": service_order.service.name,
                    "customer_name": service_order.customer_name,
                    "status": service_order.status,
                    "created_at": service_order.created_at.isoformat()
                },
                "message": f"Order {service_order.order_number} submitted successfully! Your order is now under review."
            }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to confirm service order: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to confirm service order"
            })

    @method_tool
    def get_order_status(self, order_number: str = None) -> str:
        """Get status of service orders."""
        try:
            user = getattr(self, '_user', None)
            if not user or not user.company:
                return json.dumps({
                    "status": "error",
                    "message": "User company information not available"
                })

            if order_number:
                # Get specific order
                try:
                    order = ServiceOrder.objects.get(
                        order_number=order_number,
                        company=user.company
                    )
                    return json.dumps({
                        "status": "success",
                        "company": "Wazen",
                        "order": {
                            "order_number": order.order_number,
                            "service_name": order.service.name,
                            "customer_name": order.customer_name,
                            "status": order.status,
                            "created_at": order.created_at.isoformat(),
                            "updated_at": order.updated_at.isoformat()
                        },
                        "message": f"Order {order_number} found"
                    }, ensure_ascii=False)
                except ServiceOrder.DoesNotExist:
                    return json.dumps({
                        "status": "error",
                        "message": f"Order {order_number} not found"
                    })
            else:
                # Get recent orders for this user
                orders = ServiceOrder.objects.filter(
                    created_by=user,
                    company=user.company
                ).order_by('-created_at')[:5]

                orders_data = []
                for order in orders:
                    orders_data.append({
                        "order_number": order.order_number,
                        "service_name": order.service.name,
                        "customer_name": order.customer_name,
                        "status": order.status,
                        "created_at": order.created_at.isoformat()
                    })

                return json.dumps({
                    "status": "success",
                    "company": "Wazen",
                    "orders": orders_data,
                    "count": len(orders_data),
                    "message": f"Found {len(orders_data)} recent orders"
                }, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            return json.dumps({
                "status": "error",
                "company": "Wazen",
                "error": str(e),
                "message": "Failed to get order status"
            })
