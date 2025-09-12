#!/usr/bin/env python
"""
Simple widget test without decorators
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saia.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def test_simple():
    """Simple test"""
    
    print("🧪 Simple Widget Test")
    
    client = Client()
    
    # Test if URL resolves
    try:
        url = reverse('widget:config', kwargs={'company_slug': 'wazen'})
        print(f"✅ URL resolved: {url}")
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        return
    
    # Test with minimal request
    try:
        response = client.get(url)
        print(f"📡 GET {url} -> Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Response content: {response.content.decode()}")
        else:
            print(f"✅ Success: {response.json()}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple()
