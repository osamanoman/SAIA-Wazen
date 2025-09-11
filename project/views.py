import json
import logging
from http.client import responses

from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
import uuid
import json
from django_ai_assistant.api.schemas import (ThreadIn, ThreadMessageIn)
from django_ai_assistant.helpers.use_cases import (
    create_message,
    create_thread,
    update_thread,
    delete_thread,
    get_thread_messages,
    get_threads,
)
from django_ai_assistant.models import Thread
from product.ai_tools_registry import AIToolsRegistry
# Import AI assistants
from product.ai_assistants import ProductAIAssistant
from product.assistants import COMPANY_ASSISTANTS
from company.models import Company
# Import our custom permission functions for security
from saia.permissions import (
    ai_assistant_can_create_thread,
    ai_assistant_can_view_thread,
    ai_assistant_can_create_message,
)
from pydantic import ValidationError
from django.http import QueryDict
# Keep project-specific security functions
from .security import (
    log_security_event,
    sanitize_message_content
)

# Create your views here.

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    """Simple home page view that doesn't require authentication"""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'SAIA Business Management System',
            'description': 'Welcome to the SAIA Business Management System with AI Assistant',
        })
        return context

class BaseAIAssistantView(LoginRequiredMixin, TemplateView):
    def get_assistant_id(self, **kwargs):
        """
        Enhanced routing logic that considers company AI configuration preferences.

        Returns the appropriate AI assistant based on:
        - User type (admin vs customer)
        - Company AI configuration preferences
        - Session-selected company
        - Fallback logic for unconfigured companies
        """
        user = self.request.user

        # Get company context (from session or user)
        company = self._get_user_company_context(user)

        # Enhanced routing logic
        return self._route_to_assistant(user, company)

    def _get_user_company_context(self, user):
        """Get company context from session or user"""
        # Check if user has selected a company in session (from customer selection)
        selected_company_id = self.request.session.get('selected_company_id')
        if selected_company_id:
            try:
                from company.models import Company
                return Company.objects.get(id=selected_company_id)
            except Company.DoesNotExist:
                logger.warning(f"Selected company {selected_company_id} not found in session")
                # Clear invalid session data
                self.request.session.pop('selected_company_id', None)
                self.request.session.pop('selected_company_name', None)

        # Get company from user if customer
        if hasattr(user, 'is_customer') and user.is_customer and hasattr(user, 'company'):
            return user.company

        return None

    def _route_to_assistant(self, user, company):
        """Enhanced routing logic with company configuration support"""
        # Check if admin user has explicitly selected a company via session
        selected_company_id = self.request.session.get('selected_company_id')

        # Priority 1: Check for company-specific assistant (for both admin and customer users)
        if company and hasattr(company, 'get_company_assistant_id'):
            company_assistant_id = company.get_company_assistant_id()
            if company_assistant_id:
                logger.info(f"Routing user {user.username} to company-specific assistant {company_assistant_id} for {company.name}")
                return company_assistant_id

        # Priority 2: Admin users with valid session-selected company get company-specific assistant
        if (hasattr(user, 'is_superuser') and user.is_superuser and
            selected_company_id and company):
            # Check if company has dedicated assistant
            company_assistant_id = company.get_company_assistant_id()
            if company_assistant_id and company_assistant_id in COMPANY_ASSISTANTS:
                logger.info(f"Routing admin user {user.username} to {company_assistant_id} for selected company {company.name}")
                return company_assistant_id
            else:
                # Fallback to Wazen assistant for admin users
                logger.info(f"Routing admin user {user.username} to wazen_ai_assistant for selected company {company.name}")
                return "wazen_ai_assistant"

        # Priority 3: Admin users without session-selected company get system admin assistant
        # (This includes cases where session company was invalid and cleared)
        if hasattr(user, 'is_superuser') and user.is_superuser:
            logger.info(f"Routing admin user {user.username} to ProductAIAssistant")
            return ProductAIAssistant.id

        # Priority 4: Customer users get their company-specific assistant
        if hasattr(user, 'is_customer') and user.is_customer:
            # Check if user's company has dedicated assistant
            if company:
                company_assistant_id = company.get_company_assistant_id()
                if company_assistant_id and company_assistant_id in COMPANY_ASSISTANTS:
                    logger.info(f"Routing customer user {user.username} to {company_assistant_id} for company {company.name}")
                    return company_assistant_id

            # Fallback to Wazen assistant for customer users
            logger.info(f"Routing customer user {user.username} to wazen_ai_assistant" +
                       (f" for company {company.name}" if company else ""))
            return "wazen_ai_assistant"

        # Fallback to system admin assistant for any other case
        logger.info(f"Fallback routing user {user.username} to ProductAIAssistant")
        return ProductAIAssistant.id

    def _get_company_ai_info(self, company):
        """Get AI configuration information for a company with fallback logic"""
        if not company:
            return None

        # Apply fallback logic for unconfigured companies
        ai_info = self._apply_company_ai_fallbacks(company)

        return {
            'company_name': company.name,
            'ai_language': ai_info['ai_language'],
            'ai_temperature': ai_info['ai_temperature'],
            'has_custom_instructions': ai_info['has_custom_instructions'],
            'enabled_tools_count': ai_info['enabled_tools_count'],
            'has_custom_database': ai_info['has_custom_database'],
            'subscription_status': ai_info['subscription_status'],
            'is_configured': ai_info['is_configured'],
            'fallback_applied': ai_info['fallback_applied'],
        }

    def _apply_company_ai_fallbacks(self, company):
        """Apply fallback logic for companies without AI configuration"""
        fallback_applied = []

        # Check AI language with fallback
        ai_language = getattr(company, 'ai_language', None)
        if not ai_language or ai_language == 'en':
            ai_language = 'en'  # Default fallback
            if not getattr(company, 'ai_language', None):
                fallback_applied.append('language')

        # Check AI temperature with fallback
        ai_temperature = getattr(company, 'ai_temperature', None)
        if ai_temperature is None:
            ai_temperature = 0.1  # Default fallback
            fallback_applied.append('temperature')

        # Check custom instructions
        has_custom_instructions = bool(getattr(company, 'ai_instructions_template', None))
        if not has_custom_instructions:
            fallback_applied.append('instructions')

        # Check enabled tools with fallback
        enabled_tools_count = 0
        if hasattr(company, 'get_enabled_tools'):
            try:
                enabled_tools = company.get_enabled_tools()
                enabled_tools_count = len(enabled_tools) if enabled_tools else 0
                if enabled_tools_count == 0:
                    fallback_applied.append('tools')
            except Exception as e:
                logger.warning(f"Error getting enabled tools for {company.name}: {e}")
                fallback_applied.append('tools')
        else:
            fallback_applied.append('tools')

        # Check custom database configuration
        has_custom_database = bool(getattr(company, 'database_config_json', None))
        if not has_custom_database:
            fallback_applied.append('database')

        # Check subscription status
        subscription_status = getattr(company, 'subscription_status', '0')

        # Determine if company is properly configured
        is_configured = len(fallback_applied) < 3  # If less than 3 fallbacks, consider configured

        return {
            'ai_language': ai_language,
            'ai_temperature': ai_temperature,
            'has_custom_instructions': has_custom_instructions,
            'enabled_tools_count': enabled_tools_count,
            'has_custom_database': has_custom_database,
            'subscription_status': subscription_status,
            'is_configured': is_configured,
            'fallback_applied': fallback_applied,
        }

    def _get_configuration_recommendations(self, company, ai_info):
        """Get configuration recommendations for companies using fallbacks"""
        if not ai_info or ai_info['is_configured']:
            return []

        recommendations = []
        fallbacks = ai_info.get('fallback_applied', [])

        if 'instructions' in fallbacks:
            recommendations.append({
                'type': 'instructions',
                'title': 'Custom AI Instructions',
                'description': f'Add custom AI instructions tailored to {company.name}\'s business needs',
                'priority': 'high'
            })

        if 'tools' in fallbacks:
            recommendations.append({
                'type': 'tools',
                'title': 'AI Tools Configuration',
                'description': f'Configure which AI tools are available for {company.name}\'s users',
                'priority': 'high'
            })

        if 'database' in fallbacks:
            recommendations.append({
                'type': 'database',
                'title': 'Custom Database Connection',
                'description': f'Connect {company.name}\'s own database for personalized data access',
                'priority': 'medium'
            })

        if 'language' in fallbacks and company.name:
            # Simple heuristic: if company name contains non-English characters, suggest language config
            if any(ord(char) > 127 for char in company.name):
                recommendations.append({
                    'type': 'language',
                    'title': 'Language Configuration',
                    'description': 'Configure AI assistant language preferences',
                    'priority': 'low'
                })

        return recommendations

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # CRITICAL SECURITY FIX: Filter threads by assistant_id to separate admin/customer contexts
        assistant_id = self.get_assistant_id(**kwargs)
        threads = list(get_threads(user=self.request.user, assistant_id=assistant_id))
        user = self.request.user

        # Enhanced context with company AI configuration
        company = self._get_user_company_context(user)
        company_ai_info = self._get_company_ai_info(company)

        selected_company_id = self.request.session.get('selected_company_id')
        selected_company_name = self.request.session.get('selected_company_name')
        is_customer_user = (hasattr(user, 'is_customer') and user.is_customer) or bool(selected_company_id)

        # Enhanced assistant type and description with AI configuration info
        if company:
            if selected_company_id:
                assistant_type = f"AI Assistant - {selected_company_name}"
                assistant_description = f"Customized AI assistant for {selected_company_name}"
            else:
                assistant_type = f"AI Assistant - {company.name}"
                assistant_description = f"Customized AI assistant for {company.name}"

            # Add AI configuration details to description
            if company_ai_info:
                config_details = []
                if company_ai_info['has_custom_instructions']:
                    config_details.append("custom instructions")
                if company_ai_info['enabled_tools_count'] > 0:
                    config_details.append(f"{company_ai_info['enabled_tools_count']} AI tools")
                if company_ai_info['ai_language'] != 'en':
                    config_details.append(f"language: {company_ai_info['ai_language']}")

                if config_details:
                    assistant_description += f" ({', '.join(config_details)})"
        else:
            if hasattr(user, 'is_customer') and user.is_customer:
                assistant_type = "Customer Data Assistant"
                assistant_description = "Access your company's database"
            else:
                assistant_type = "SAIA System Assistant"
                assistant_description = "Manage SAIA system data and operations"

        # Add custom permission context using our existing permission functions
        can_create = ai_assistant_can_create_thread(user=user, request=self.request)

        # Get configuration recommendations for unconfigured companies
        config_recommendations = []
        if company and company_ai_info and not company_ai_info.get('is_configured', True):
            config_recommendations = self._get_configuration_recommendations(company, company_ai_info)

        context.update(
            {
                "assistant_id": self.get_assistant_id(**kwargs),
                "threads": threads,
                "is_customer_user": is_customer_user,
                "assistant_type": assistant_type,
                "assistant_description": assistant_description,
                "user_company": getattr(user, 'company', None),
                "selected_company_id": selected_company_id,
                "selected_company_name": selected_company_name,
                # Enhanced: Company AI configuration information
                "company_ai_info": company_ai_info,
                "current_company": company,
                "config_recommendations": config_recommendations,
                # Custom permissions using our existing security functions
                "can_create_thread": can_create,
                "can_view_threads": user.is_authenticated,  # Basic check, per-thread checks are done in permission functions
            }
        )
        return context














class AIAssistantChatHomeView(BaseAIAssistantView):
    template_name = "admin/chat_home.html"

    def post(self, request, *args, **kwargs):

        if ai_assistant_can_create_thread(user=request.user, request=request):
            try:
                # Fix: Extract string values from QueryDict (Django returns lists)
                post_data = {
                    'name': request.POST.get('name', 'New Chat Session'),
                    'assistant_id': request.POST.get('assistant_id', None)
                }
                thread_data = ThreadIn(**post_data)
            except ValidationError as e:
                messages.error(request, "Invalid thread data")
                return redirect("chat_home")

            # CRITICAL SECURITY FIX: Create thread with proper assistant_id for context separation
            assistant_id = self.get_assistant_id()

            try:
                thread = create_thread(
                    name=thread_data.name,
                    assistant_id=assistant_id,
                    user=request.user,
                    request=request
                )
                return redirect("chat_thread", thread_id=thread.id)
            except Exception as e:
                messages.error(request, f"Error creating thread: {e}")
                return redirect("chat_home")
        else:
            messages.error(request, "عذراً لا يوجد لديك صلاحية إضافة جلسات")
            return redirect("chat_home")



class AIAssistantChatThreadView(BaseAIAssistantView):
    template_name = "admin/chat_thread.html"
    def get_context_data(self, **kwargs):
        thread_id = self.kwargs["thread_id"]
        thread = get_object_or_404(Thread, id=thread_id)

        if ai_assistant_can_view_thread(thread=thread, user=self.request.user, request=self.request):
            context = super().get_context_data(**kwargs)

            thread_messages = get_thread_messages(
                thread=thread,
                user=self.request.user,
                request=self.request,
            )

            context.update(
                {
                    "thread_id": thread_id,
                    "thread_messages": thread_messages,
                }
            )
            return context
        else:
            # User doesn't have permission to view this thread
            context = super().get_context_data(**kwargs)
            context.update({
                "thread_id": thread_id,
                "thread_messages": [],
                "permission_error": "You don't have permission to view this thread."
            })
            return context

    # POST to create message:
    def post(self, request, *args, **kwargs):
        assistant_id = self.get_assistant_id()
        thread_id = self.kwargs["thread_id"]
        thread = get_object_or_404(Thread, id=thread_id)

        # Check if user can create messages in this thread
        can_create_msg = ai_assistant_can_create_message(user=request.user, thread=thread, request=request)

        if can_create_msg:
            try:
                message = ThreadMessageIn(
                    assistant_id=assistant_id,
                    content=request.POST.get("content") or None,
                )
            except ValidationError:
                messages.error(request, "Invalid message data")
                return redirect("chat_thread", thread_id=thread_id)

            create_message(
                assistant_id=assistant_id,
                thread=thread,
                user=request.user,
                content=message.content,
                request=request,
            )
            return redirect("chat_thread", thread_id=thread_id)
        messages.error(request, "لا يوجد لديك صلاحية اضافة رسائل")
        return redirect("chat_thread", thread_id=thread_id)

    # PATCH to update thread:
    def patch(self, request, *args, **kwargs):
        thread_id = self.kwargs["thread_id"]
        thread = get_object_or_404(Thread, id=thread_id)
        qd = QueryDict(request.body)
        put_dict = {k: v[0] if len(v) == 1 else v for k, v in qd.lists()}

        thread = update_thread(
            thread=thread,
            name=put_dict.get("content") or None,
            user=request.user,
            request=request,
        )
        messages.error(request, "Invalid message data")
        return HttpResponse(thread.name,content_type="text/plain", status=204, headers={
            'HX-Trigger': json.dumps({
                'messages':
                    [
                    {
                        'messages': {'message': message.message, 'tags': message.tags},

                    }
                    for message in messages.get_messages(request)
                ]
            })
        })



# DELETE to delete thread:
    def delete(self, request, *args, **kwargs):
        thread_id = self.kwargs["thread_id"]
        thread = get_object_or_404(Thread, id=thread_id)

        delete_thread(
            thread=thread,
            user=request.user,
            request=request,
        )

        context = super().get_context_data(**kwargs)
        threads = list(get_threads(user=self.request.user))
        context.update(
            {
                "assistant_id": self.get_assistant_id(**kwargs),
                "threads": threads,
            }
        )

        return render(request, 'admin/chat_home.html',context)


