"""
URL configuration for the widget app.

This module defines all the API endpoints for the chatbot widget.
All URLs are prefixed with /api/widget/ in the main URL configuration.
"""

from django.urls import path
from . import views

app_name = 'widget'

urlpatterns = [
    # Widget configuration
    path('config/<str:company_slug>/', views.widget_config_api, name='config'),

    # Session management
    path('session/create/<str:company_slug>/', views.session_create_api, name='session_create'),
    path('session/<str:session_id>/status/', views.session_status_api, name='session_status'),
    path('session/<str:session_id>/messages/', views.session_messages_api, name='session_messages'),
    path('session/<str:session_id>/send/', views.message_send_api, name='message_send'),
    path('session/<str:session_id>/close/', views.session_close_api, name='session_close'),

    # File upload
    path('session/<str:session_id>/upload/', views.file_upload_api, name='file_upload'),

    # Session management endpoints
    path('session/<str:session_id>/clear/', views.clear_session_api, name='clear_session'),

    # Handover management
    path('session/<str:session_id>/handover/', views.handover_request_api, name='handover_request'),

    # Widget integration endpoints
    path('embed/<str:company_slug>/', views.widget_embed_view, name='widget_embed'),
    path('integration/<str:company_slug>/', views.widget_integration_code_view, name='widget_integration'),
    path('demo/<str:company_slug>/', views.widget_demo_view, name='widget_demo'),
    path('demo/', views.widget_demo_view, name='widget_demo_default'),
]
