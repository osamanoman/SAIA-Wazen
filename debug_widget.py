#!/usr/bin/env python
"""
Debug script for widget API issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saia.settings')
django.setup()

from company.models import Company
from widget.helpers import get_company_by_slug

def debug_company_lookup():
    """Debug company lookup"""
    
    print("🔍 Debugging company lookup...")
    
    # List all companies
    companies = Company.objects.all()
    print(f"📋 Found {companies.count()} companies:")
    for company in companies:
        print(f"   - {company.name} (ID: {company.id})")
    
    # Test helper function
    print(f"\n🧪 Testing get_company_by_slug('wazen')...")
    company = get_company_by_slug('wazen')
    if company:
        print(f"✅ Found company: {company.name}")
    else:
        print("❌ Company not found")
    
    # Test different variations
    test_slugs = ['wazen', 'Wazen', 'WAZEN', 'wazen-company']
    for slug in test_slugs:
        company = get_company_by_slug(slug)
        print(f"   - '{slug}' -> {company.name if company else 'Not found'}")

def debug_widget_view():
    """Debug widget view directly"""
    
    print("\n🔍 Debugging widget view directly...")
    
    from widget.views import widget_config_api
    from django.http import HttpRequest
    
    # Create mock request
    request = HttpRequest()
    request.method = 'GET'
    request.META = {'HTTP_ORIGIN': 'http://localhost:3000'}
    
    try:
        response = widget_config_api(request, 'wazen')
        print(f"✅ Direct view call successful: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"📄 Response content: {response.content.decode()[:200]}...")
    except Exception as e:
        print(f"❌ Direct view call failed: {e}")
        import traceback
        traceback.print_exc()

def debug_security_decorators():
    """Debug security decorators"""
    
    print("\n🔍 Debugging security decorators...")
    
    from widget.security import rate_limit
    from django.http import HttpRequest
    from django.core.cache import cache
    
    # Clear cache
    cache.clear()
    print("✅ Cache cleared")
    
    # Test rate limiting
    request = HttpRequest()
    request.META = {
        'REMOTE_ADDR': '127.0.0.1',
        'HTTP_X_FORWARDED_FOR': '127.0.0.1'
    }
    
    print("✅ Security decorators check complete")

if __name__ == '__main__':
    debug_company_lookup()
    debug_security_decorators()
    debug_widget_view()
