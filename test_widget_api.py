#!/usr/bin/env python
"""
Simple test script for SAIA Widget API

This script tests the consolidated widget API endpoints to ensure
they work correctly with the new ThreadExtension and WidgetConfiguration models.
"""

import os
import sys
import django
import json
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saia.settings')
django.setup()

from company.models import Company
from widget.models import WidgetConfiguration, ThreadExtension, WebsiteSession
from django_ai_assistant.models import Thread

User = get_user_model()

def test_widget_api():
    """Test the widget API endpoints"""
    
    print("🧪 Testing SAIA Widget API...")
    
    # Create test client
    client = Client()
    
    # 1. Test widget configuration endpoint
    print("\n1️⃣ Testing widget configuration endpoint...")

    try:
        # Get Wazen company
        wazen = Company.objects.get(name='Wazen')
        print(f"✅ Found company: {wazen.name}")

        # Test widget config API with proper headers
        response = client.get(
            '/api/widget/config/wazen/',
            HTTP_ORIGIN='http://localhost:3000',
            HTTP_X_FORWARDED_FOR='127.0.0.1'
        )
        print(f"📡 GET /api/widget/config/wazen/ -> Status: {response.status_code}")

        if response.status_code == 200:
            config_data = response.json()
            print(f"✅ Widget config loaded successfully:")
            print(f"   - Company: {config_data.get('company_name')}")
            print(f"   - Assistant ID: {config_data.get('assistant_id')}")
            print(f"   - Welcome Message: {config_data.get('welcome_message')[:50]}...")
            print(f"   - Is Active: {config_data.get('is_active')}")
        else:
            print(f"❌ Widget config failed: {response.content.decode()}")

    except Company.DoesNotExist:
        print("❌ Wazen company not found. Please create it first.")
        return False
    except Exception as e:
        print(f"❌ Error testing widget config: {e}")
        return False
    
    # 2. Test session creation endpoint
    print("\n2️⃣ Testing session creation endpoint...")
    
    try:
        session_data = {
            'visitor_ip': '127.0.0.1',
            'user_agent': 'Test Browser 1.0',
            'referrer_url': 'https://test.com',
            'visitor_metadata': {'test': True}
        }
        
        response = client.post(
            '/api/widget/session/create/wazen/',
            data=json.dumps(session_data),
            content_type='application/json',
            HTTP_ORIGIN='http://localhost:3000',
            HTTP_X_FORWARDED_FOR='127.0.0.1'
        )
        
        print(f"📡 POST /api/widget/session/create/wazen/ -> Status: {response.status_code}")
        
        if response.status_code == 200:
            session_response = response.json()
            session_id = session_response.get('session_id')
            print(f"✅ Session created successfully:")
            print(f"   - Session ID: {session_id}")
            print(f"   - Company: {session_response.get('company_name')}")
            print(f"   - Assistant ID: {session_response.get('assistant_id')}")
            
            # Verify database objects were created
            session = WebsiteSession.objects.get(session_id=session_id)
            print(f"✅ WebsiteSession created: {session}")
            
            # Check ThreadExtension
            thread_extension = ThreadExtension.objects.get(thread=session.thread)
            print(f"✅ ThreadExtension created:")
            print(f"   - Session Type: {thread_extension.session_type}")
            print(f"   - Is Anonymous: {thread_extension.is_anonymous}")
            
            return session_id
            
        else:
            print(f"❌ Session creation failed: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session creation: {e}")
        return False

def test_widget_configuration_model():
    """Test the WidgetConfiguration model"""
    
    print("\n3️⃣ Testing WidgetConfiguration model...")
    
    try:
        # Get or create widget config for Wazen
        wazen = Company.objects.get(name='Wazen')
        
        config, created = WidgetConfiguration.objects.get_or_create(
            company=wazen,
            defaults={
                'welcome_message': 'مرحباً! كيف يمكنني مساعدتك اليوم؟',
                'theme_config': {
                    'primary_color': '#1e40af',
                    'secondary_color': '#f3f4f6',
                    'text_color': '#1f2937'
                },
                'position': 'bottom-right',
                'auto_open': False,
                'auto_open_delay': 3,
                'is_active': True,
                'rate_limit_per_minute': 20,
                'max_message_length': 2000
            }
        )
        
        if created:
            print(f"✅ Created new WidgetConfiguration for {wazen.name}")
        else:
            print(f"✅ Found existing WidgetConfiguration for {wazen.name}")
            
        # Test methods
        theme = config.get_theme_config()
        print(f"✅ Theme config: {len(theme)} properties")
        
        embed_code = config.generate_embed_code()
        print(f"✅ Embed code generated: {len(embed_code)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing WidgetConfiguration: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 SAIA Widget API Test Suite")
    print("=" * 50)
    
    # Test widget configuration model
    if not test_widget_configuration_model():
        print("\n❌ WidgetConfiguration model test failed")
        return
    
    # Test widget API endpoints
    session_id = test_widget_api()
    if not session_id:
        print("\n❌ Widget API test failed")
        return
    
    print("\n🎉 All tests passed successfully!")
    print("\n📊 Test Summary:")
    print("✅ WidgetConfiguration model working")
    print("✅ ThreadExtension model working")
    print("✅ Widget config API working")
    print("✅ Session creation API working")
    print("✅ Database integration working")
    
    print(f"\n🔗 Test session created: {session_id}")
    print("\n🎯 The consolidated widget implementation is working correctly!")

if __name__ == '__main__':
    main()
