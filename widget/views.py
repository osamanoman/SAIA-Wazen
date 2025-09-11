import json
import uuid
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django_ai_assistant.models import Thread, Message
from django_ai_assistant.helpers.use_cases import create_message

from company.models import Company
from .models import WebsiteSession, SessionHandover
from .security import rate_limit, validate_widget_request, add_cors_headers

User = get_user_model()
logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
@rate_limit('widget_config')
def widget_config_api(request, company_slug):
    """
    Get widget configuration for a company.

    Returns widget theme, welcome message, and other configuration.
    This endpoint is called when the widget loads on a website.
    """
    try:
        # Validate company slug format
        if not company_slug.replace('-', '').replace('_', '').isalnum():
            return JsonResponse({
                "error": "Invalid company identifier",
                "message": "Company identifier contains invalid characters"
            }, status=400)

        # Get company
        company = Company.objects.get(name__iexact=company_slug)

        # Get company-specific AI assistant (same as admin interface)
        assistant_id = company.get_company_assistant_id()

        # Prepare response data
        response_data = {
            "company_name": company.name,
            "assistant_id": assistant_id,
            "welcome_message": company.get_widget_welcome_message(),
            "theme_config": company.get_widget_theme_config(),
            "position": company.widget_position or "bottom-right",
            "is_active": company.widget_is_active
        }

        response = JsonResponse(response_data)
        return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))

    except Company.DoesNotExist:
        return JsonResponse({"error": f"Company '{company_slug}' not found"}, status=404)
    except Exception as e:
        logger.error(f"Error getting widget config for {company_slug}: {e}")
        return JsonResponse({"error": "Failed to load widget configuration"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit('session_create')
@validate_widget_request(['visitor_ip'])
def session_create_api(request, company_slug):
    """
    Create a new chat session for a website visitor.

    Creates an anonymous user, AI thread, and website session.
    Returns session ID and initial configuration.
    """
    try:
        # Validate company slug format
        if not company_slug.replace('-', '').replace('_', '').isalnum():
            return JsonResponse({
                "error": "Invalid company identifier",
                "message": "Company identifier contains invalid characters"
            }, status=400)

        # Parse request data
        data = json.loads(request.body)
        visitor_ip = data.get('visitor_ip')

        # Get company
        company = Company.objects.get(name__iexact=company_slug)

        # Get company-specific AI assistant (using same logic as admin interface)
        assistant_id = company.get_company_assistant_id()
        if not assistant_id:
            return JsonResponse({
                "error": "AI assistant not available",
                "details": f"No AI assistant configured for {company.name}"
            }, status=503)

        # Verify assistant exists (using the same logic as project views)
        from product.assistants import COMPANY_ASSISTANTS
        if assistant_id not in COMPANY_ASSISTANTS:
            return JsonResponse({
                "error": "AI assistant not available",
                "details": f"Company assistant '{assistant_id}' is not configured"
            }, status=503)

        # Create or get company-specific anonymous user for widget sessions
        anonymous_username = f'widget_anonymous_{company.name.lower()}'
        anonymous_user, created = User.objects.get_or_create(
            username=anonymous_username,
            defaults={
                'email': f'anonymous@{company.name.lower()}.widget',
                'first_name': 'Anonymous',
                'last_name': f'{company.name} Widget User',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
                'is_customer': True,  # Mark as customer user for permission system
                'company': company  # Assign to company for AI assistant verification
            }
        )

        # Ensure the user is properly configured (in case it was created before)
        if not anonymous_user.company or not anonymous_user.is_customer:
            anonymous_user.company = company
            anonymous_user.is_customer = True  # Ensure customer flag is set
            anonymous_user.save()

        # Create thread using existing logic (with anonymous user as owner)
        thread_name = f"{company.name} Website Visitor {uuid.uuid4().hex[:8]}"
        thread = Thread.objects.create(
            name=thread_name,
            created_by=anonymous_user,  # Anonymous user owns the thread
            assistant_id=assistant_id
        )

        # Create website session
        website_session = WebsiteSession.objects.create(
            session_id=uuid.uuid4(),
            thread=thread,
            company=company,
            visitor_ip=visitor_ip,
            user_agent=data.get('user_agent', ''),
            referrer_url=data.get('referrer_url', ''),
            visitor_metadata=data.get('visitor_metadata', {})
        )

        logger.info(f"Created website session {website_session.session_id} for {company.name}")

        response = JsonResponse({
            "session_id": str(website_session.session_id),
            "company_name": company.name,
            "assistant_id": thread.assistant_id,
            "welcome_message": company.get_widget_welcome_message(),
            "theme_config": company.get_widget_theme_config()
        })

        return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))

    except Company.DoesNotExist:
        return JsonResponse({"error": f"Company '{company_slug}' not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        logger.error(f"Error creating session for {company_slug}: {e}")
        return JsonResponse({"error": "Failed to create chat session"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit('message_send')
@validate_widget_request(['content'])
def message_send_api(request, session_id):
    """
    Send a message in a chat session.

    Processes user message and returns AI response.
    """
    try:
        # Validate session ID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            return JsonResponse({
                "error": "Invalid session ID format",
                "message": "Session ID must be a valid UUID"
            }, status=400)

        # Parse request data
        data = json.loads(request.body)
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({"error": "Message content cannot be empty"}, status=400)

        # Get website session
        try:
            website_session = WebsiteSession.objects.get(session_id=session_id)
        except WebsiteSession.DoesNotExist:
            return JsonResponse({"error": "Session not found"}, status=404)

        # Check if session is active
        if not website_session.is_active:
            return JsonResponse({"error": "Session is not active"}, status=400)

        # Get the same anonymous user that owns the thread
        # This should be the same user created during session creation
        company = website_session.company
        anonymous_username = f'widget_anonymous_{company.name.lower()}'

        try:
            anonymous_user = User.objects.get(username=anonymous_username)
        except User.DoesNotExist:
            # Fallback: create the user if it doesn't exist (shouldn't happen)
            anonymous_user = User.objects.create(
                username=anonymous_username,
                email=f'anonymous@{company.name.lower()}.widget',
                first_name='Anonymous',
                last_name=f'{company.name} Widget User',
                is_active=True,
                is_staff=False,
                is_superuser=False,
                is_customer=True,  # Mark as customer user
                company=company
            )

        # Create AI message using the same logic as project views
        ai_response = create_message(
            assistant_id=website_session.thread.assistant_id,
            thread=website_session.thread,
            user=anonymous_user,
            content=content,
            request=request
        )

        logger.info(f"Message sent in session {session_id}: {len(content)} chars")

        # Get the latest message from the thread (should be the AI response)
        latest_message = website_session.thread.messages.order_by('-created_at').first()

        # Return the AI response
        if latest_message:
            # Extract content from the message data structure
            message_content = latest_message.message
            content = ""

            if isinstance(message_content, dict):
                # Handle nested data structure from AI response
                if 'data' in message_content and isinstance(message_content['data'], dict):
                    # Extract from nested data structure
                    data_content = message_content['data']
                    if 'content' in data_content:
                        content = data_content['content']
                    else:
                        content = str(data_content)
                elif 'content' in message_content:
                    # Direct content field
                    content = message_content['content']
                else:
                    # Fallback to string representation
                    content = str(message_content)
            else:
                content = str(message_content)

            response_data = {
                "id": str(latest_message.id),
                "content": content,
                "message_type": "ai",
                "timestamp": latest_message.created_at.isoformat(),
                "is_ai": True
            }
        else:
            response_data = {
                "id": None,
                "content": "AI response generated successfully",
                "message_type": "ai",
                "timestamp": None,
                "is_ai": True
            }

        response = JsonResponse(response_data)
        return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        logger.error(f"Error sending message to session {session_id}: {e}")
        return JsonResponse({"error": "Failed to send message"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def session_status_api(request, session_id):
    """
    Get status and information about a chat session.
    """
    try:
        # Validate session ID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            return JsonResponse({
                "error": "Invalid session ID format",
                "message": "Session ID must be a valid UUID"
            }, status=400)

        # Get website session
        try:
            website_session = WebsiteSession.objects.get(session_id=session_id)
        except WebsiteSession.DoesNotExist:
            return JsonResponse({"error": "Session not found"}, status=404)

        # Prepare response data
        response_data = {
            "session_id": str(website_session.session_id),
            "status": website_session.status,
            "is_active": website_session.is_active,
            "is_expired": website_session.is_expired,
            "created_at": website_session.created_at.isoformat(),
            "last_activity": website_session.last_activity.isoformat(),
            "message_count": website_session.get_message_count(),
            "duration_minutes": website_session.duration_minutes,
            "company_name": website_session.company.name
        }

        response = JsonResponse(response_data)
        return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))

    except Exception as e:
        logger.error(f"Error getting session status {session_id}: {e}")
        return JsonResponse({"error": "Failed to get session status"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def session_messages_api(request, session_id):
    """
    Get all messages in a chat session.
    """
    try:
        # Validate session ID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            return JsonResponse({
                "error": "Invalid session ID format",
                "message": "Session ID must be a valid UUID"
            }, status=400)

        # Get website session
        try:
            website_session = WebsiteSession.objects.get(session_id=session_id)
        except WebsiteSession.DoesNotExist:
            return JsonResponse({"error": "Session not found"}, status=404)

        # Get messages from the thread with pagination
        limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 messages per request
        offset = int(request.GET.get('offset', 0))

        messages = website_session.thread.messages.order_by('created_at')[offset:offset+limit]
        total_messages = website_session.thread.messages.count()

        # Format messages for response
        message_list = []
        for message in messages:
            # Determine message type and extract content
            message_content = message.message
            content = ""
            message_type = 'human'  # Default

            if isinstance(message_content, dict):
                # Handle nested data structure
                if 'data' in message_content and isinstance(message_content['data'], dict):
                    data_content = message_content['data']
                    # Check message type from nested data
                    if data_content.get('type') == 'ai':
                        message_type = 'ai'
                    elif data_content.get('type') == 'human':
                        message_type = 'human'
                    elif data_content.get('type') == 'tool':
                        # Skip tool messages for now
                        continue

                    # Extract content from nested data
                    if 'content' in data_content:
                        content = data_content['content']
                    else:
                        content = str(data_content)

                elif message_content.get('type') == 'ai':
                    message_type = 'ai'
                    content = message_content.get('content', str(message_content))
                elif message_content.get('type') == 'human':
                    message_type = 'human'
                    content = message_content.get('content', str(message_content))
                else:
                    # Try to extract content directly
                    content = message_content.get('content', str(message_content))
            else:
                # Simple string message
                content = str(message_content)

            message_data = {
                "id": str(message.id),
                "content": content,
                "message_type": message_type,
                "timestamp": message.created_at.isoformat(),
                "is_ai": message_type == 'ai'
            }
            message_list.append(message_data)

        response_data = {
            "session_id": str(website_session.session_id),
            "messages": message_list,
            "total_messages": total_messages,
            "returned_messages": len(message_list),
            "session_status": website_session.status,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_messages
            }
        }

        response = JsonResponse(response_data)
        return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))

    except Exception as e:
        logger.error(f"Error getting messages for session {session_id}: {e}")
        return JsonResponse({"error": "Failed to get session messages"}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
@validate_widget_request([])
def session_close_api(request, session_id):
    """
    Close a chat session.
    """
    try:
        # Validate session ID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            return JsonResponse({
                "error": "Invalid session ID format",
                "message": "Session ID must be a valid UUID"
            }, status=400)

        # Parse request data
        data = json.loads(request.body) if request.body else {}
        reason = data.get('reason', 'user_closed')

        # Get website session
        try:
            website_session = WebsiteSession.objects.get(session_id=session_id)
        except WebsiteSession.DoesNotExist:
            return JsonResponse({"error": "Session not found"}, status=404)

        # Close the session
        website_session.close_session(reason=reason)

        logger.info(f"Closed session {session_id} - reason: {reason}")

        response_data = {
            "session_id": str(website_session.session_id),
            "status": website_session.status,
            "closed_at": website_session.closed_at.isoformat(),
            "message": "Session closed successfully"
        }

        response = JsonResponse(response_data)
        return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        logger.error(f"Error closing session {session_id}: {e}")
        return JsonResponse({"error": "Failed to close session"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit('handover_request')
@validate_widget_request(['reason'])
def handover_request_api(request, session_id):
    """
    Request handover to human agent.
    """
    try:
        # Validate session ID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            return JsonResponse({
                "error": "Invalid session ID format",
                "message": "Session ID must be a valid UUID"
            }, status=400)

        # Parse request data
        data = json.loads(request.body)
        reason = data.get('reason', '').strip()
        priority = data.get('priority', 'medium')

        if not reason:
            return JsonResponse({"error": "Handover reason is required"}, status=400)

        # Get website session
        try:
            website_session = WebsiteSession.objects.get(session_id=session_id)
        except WebsiteSession.DoesNotExist:
            return JsonResponse({"error": "Session not found"}, status=404)

        # Check if session is active
        if not website_session.is_active:
            return JsonResponse({"error": "Session is not active"}, status=400)

        # Create handover request
        handover = SessionHandover.objects.create(
            session=website_session,
            reason=reason,
            priority=priority
        )

        logger.info(f"Handover requested for session {session_id}: {reason}")

        response_data = {
            "handover_id": str(handover.id),
            "session_id": str(website_session.session_id),
            "status": handover.status,
            "priority": handover.priority,
            "requested_at": handover.requested_at.isoformat(),
            "message": "Handover request created successfully"
        }

        response = JsonResponse(response_data)
        return add_cors_headers(response, request.META.get('HTTP_ORIGIN'))

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        logger.error(f"Error requesting handover for session {session_id}: {e}")
        return JsonResponse({"error": "Failed to request handover"}, status=500)


# ==================== WIDGET INTEGRATION VIEWS ====================

def widget_embed_view(request, company_slug):
    """
    Generate the widget embed HTML for a specific company.
    This view provides the integration code that websites can embed.
    """
    try:
        # Get company configuration
        company = get_object_or_404(Company, name__iexact=company_slug)

        if not company.widget_is_active:
            return JsonResponse({"error": "Widget is not active for this company"}, status=403)

        # Get configuration from query parameters
        position = request.GET.get('position', 'bottom-right')
        auto_open = request.GET.get('auto_open', 'false').lower() == 'true'
        show_welcome_message = request.GET.get('show_welcome_message', 'true').lower() == 'true'
        enable_sound = request.GET.get('enable_sound', 'true').lower() == 'true'
        theme = request.GET.get('theme', 'default')
        debug = request.GET.get('debug', 'false').lower() == 'true'
        max_messages = int(request.GET.get('max_messages', '100'))
        session_timeout = int(request.GET.get('session_timeout', '1800000'))  # 30 minutes

        # Build asset URLs
        api_base_url = request.build_absolute_uri('/').rstrip('/')
        widget_css_url = request.build_absolute_uri('/static/widget/css/saia-widget.css')
        widget_js_url = request.build_absolute_uri('/static/widget/js/saia-widget.js')

        context = {
            'company_slug': company_slug,
            'api_base_url': api_base_url,
            'widget_css_url': widget_css_url,
            'widget_js_url': widget_js_url,
            'position': position,
            'auto_open': auto_open,
            'show_welcome_message': show_welcome_message,
            'enable_sound': enable_sound,
            'theme': theme,
            'debug': debug,
            'max_messages': max_messages,
            'session_timeout': session_timeout,
            'analytics_enabled': request.GET.get('analytics', 'false').lower() == 'true',
            'custom_css': request.GET.get('custom_css', ''),
            'on_ready_callback': request.GET.get('on_ready', ''),
            'on_open_callback': request.GET.get('on_open', ''),
            'on_close_callback': request.GET.get('on_close', ''),
            'on_message_callback': request.GET.get('on_message', ''),
            'on_error_callback': request.GET.get('on_error', ''),
        }

        return render(request, 'widget/embed.html', context, content_type='text/html')

    except Company.DoesNotExist:
        return JsonResponse({"error": f"Company '{company_slug}' not found"}, status=404)
    except Exception as e:
        logger.error(f"Error generating embed for {company_slug}: {e}")
        return JsonResponse({"error": "Failed to generate embed code"}, status=500)


def widget_integration_code_view(request, company_slug):
    """
    Generate integration code snippets for different integration methods.
    """
    try:
        # Get company configuration
        company = get_object_or_404(Company, name__iexact=company_slug)

        if not company.widget_is_active:
            return JsonResponse({"error": "Widget is not active for this company"}, status=403)

        # Build URLs
        api_base_url = request.build_absolute_uri('/').rstrip('/')
        loader_url = request.build_absolute_uri('/static/widget/js/saia-widget-loader.js')
        embed_url = request.build_absolute_uri(f'/widget/embed/{company_slug}/')

        # Generate different integration methods
        integration_methods = {
            'simple_script_tag': f'''<!-- Simple Script Tag Integration -->
<script
    src="{loader_url}"
    data-company="{company_slug}"
    data-api-url="{api_base_url}"
    data-position="bottom-right"
    data-auto-open="false"
    data-theme="default"
    async>
</script>''',

            'advanced_javascript': f'''<!-- Advanced JavaScript Integration -->
<script>
(function(w,d,s,o,f,js,fjs){{
    w['SAIAWidgetObject']=o;w[o]=w[o]||function(){{(w[o].q=w[o].q||[]).push(arguments)}};
    js=d.createElement(s),fjs=d.getElementsByTagName(s)[0];
    js.id=o;js.src=f;js.async=1;fjs.parentNode.insertBefore(js,fjs);
}})(window,document,'script','saia','{loader_url}');

saia('init', {{
    companySlug: '{company_slug}',
    apiBaseUrl: '{api_base_url}',
    position: 'bottom-right',
    autoOpen: false,
    showWelcomeMessage: true,
    enableSound: true,
    theme: 'default',
    debug: false,

    // Event callbacks
    onReady: function(widget) {{
        console.log('SAIA Widget ready!');
    }},
    onOpen: function(widget) {{
        console.log('Widget opened');
    }},
    onMessage: function(message, widget) {{
        console.log('New message:', message);
    }}
}});
</script>''',

            'iframe_embed': f'''<!-- iFrame Embed (Alternative Method) -->
<iframe
    src="{embed_url}?position=bottom-right&auto_open=false"
    width="400"
    height="600"
    frameborder="0"
    style="position: fixed; bottom: 20px; right: 20px; z-index: 999999; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
</iframe>''',

            'react_component': f'''// React Component Integration
import {{ useEffect }} from 'react';

function SAIAWidget() {{
    useEffect(() => {{
        // Load SAIA Widget
        const script = document.createElement('script');
        script.src = '{loader_url}';
        script.async = true;
        document.head.appendChild(script);

        script.onload = () => {{
            window.saia('init', {{
                companySlug: '{company_slug}',
                apiBaseUrl: '{api_base_url}',
                position: 'bottom-right',
                autoOpen: false
            }});
        }};

        return () => {{
            // Cleanup
            if (window.saia) {{
                window.saia('destroy');
            }}
        }};
    }}, []);

    return null; // Widget renders itself
}}

export default SAIAWidget;''',

            'wordpress_plugin': f'''<!-- WordPress Integration -->
<!-- Add this to your theme's functions.php file -->
<?php
function add_saia_widget() {{
    ?>
    <script
        src="{loader_url}"
        data-company="{company_slug}"
        data-api-url="{api_base_url}"
        data-position="bottom-right"
        async>
    </script>
    <?php
}}
add_action('wp_footer', 'add_saia_widget');
?>'''
        }

        return JsonResponse({
            'company': company.name,
            'integration_methods': integration_methods,
            'urls': {
                'api_base': api_base_url,
                'loader_script': loader_url,
                'embed_page': embed_url
            },
            'configuration_options': {
                'position': ['bottom-right', 'bottom-left', 'top-right', 'top-left'],
                'theme': ['default', 'modern', 'minimal', 'corporate'],
                'auto_open': [True, False],
                'show_welcome_message': [True, False],
                'enable_sound': [True, False]
            }
        })

    except Company.DoesNotExist:
        return JsonResponse({"error": f"Company '{company_slug}' not found"}, status=404)
    except Exception as e:
        logger.error(f"Error generating integration code for {company_slug}: {e}")
        return JsonResponse({"error": "Failed to generate integration code"}, status=500)


def widget_demo_view(request, company_slug='wazen'):
    """
    Serve the widget demo page through Django to avoid CORS issues.
    """
    try:
        # Get company configuration
        company = get_object_or_404(Company, name__iexact=company_slug)

        if not company.widget_is_active:
            return JsonResponse({"error": "Widget is not active for this company"}, status=403)

        # Build asset URLs
        api_base_url = request.build_absolute_uri('/').rstrip('/')
        loader_url = request.build_absolute_uri('/static/widget/js/saia-widget-loader.js')

        context = {
            'company_slug': company_slug,
            'api_base_url': api_base_url,
            'loader_url': loader_url,
        }

        return render(request, 'widget/demo.html', context, content_type='text/html')

    except Company.DoesNotExist:
        return JsonResponse({"error": f"Company '{company_slug}' not found"}, status=404)
    except Exception as e:
        logger.error(f"Error serving demo for {company_slug}: {e}")
        return JsonResponse({"error": "Failed to serve demo page"}, status=500)
