"""
URL Configuration for SAIA Multi-Tenant Website Chatbot Platform
"""

from django.urls import path, include
from .api import widget_api

app_name = 'chatbot'

urlpatterns = [
    # Public Widget API (no authentication required)
    path('api/widget/', widget_api.urls),
]
