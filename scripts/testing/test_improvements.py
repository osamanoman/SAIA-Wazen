#!/usr/bin/env python
"""
Test script for the service ordering improvements:
- Phone number validation
- Full name validation  
- ID validation (10 digits)
- Image upload verification
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saia.settings')
django.setup()

from product.assistants.wazen_ai_assistant import WazenAIAssistant
from users.models import User
from company.models import Company
import json

def test_validations():
    """Test the new validation rules"""
    print("🧪 TESTING SERVICE ORDERING IMPROVEMENTS")
    print("=" * 50)
    
    try:
        # Get Wazen user for testing
        wazen_company = Company.objects.get(name='Wazen')
        wazen_user = User.objects.filter(company=wazen_company).first()
        
        if not wazen_user:
            print("❌ No Wazen user found for testing")
            return
            
        print(f"👤 Testing with user: {wazen_user.username}")
        
        # Create AI assistant instance
        assistant = WazenAIAssistant()
        assistant._user = wazen_user
        
        print("\n📱 TESTING PHONE NUMBER VALIDATION:")
        print("-" * 30)
        
        # Test valid phone numbers
        valid_phones = ["512345678", "0512345678"]
        for phone in valid_phones:
            result = assistant.collect_customer_phone(phone)
            data = json.loads(result)
            print(f"✅ {phone}: {data.get('status', 'unknown')}")
            
        # Test invalid phone numbers
        invalid_phones = ["123456789", "05123", "abc123456", "612345678"]
        for phone in invalid_phones:
            result = assistant.collect_customer_phone(phone)
            data = json.loads(result)
            print(f"❌ {phone}: {data.get('message', 'unknown error')}")
            
        print("\n👤 TESTING NAME VALIDATION:")
        print("-" * 25)
        
        # Test valid names
        valid_names = ["أحمد محمد", "Ahmed Ali", "فاطمة عبدالله السعودي"]
        for name in valid_names:
            result = assistant.collect_customer_name(name)
            data = json.loads(result)
            print(f"✅ '{name}': {data.get('status', 'unknown')}")
            
        # Test invalid names (single word)
        invalid_names = ["أحمد", "Ahmed", "123"]
        for name in invalid_names:
            result = assistant.collect_customer_name(name)
            data = json.loads(result)
            print(f"❌ '{name}': {data.get('message', 'unknown error')}")
            
        print("\n🆔 TESTING ID VALIDATION:")
        print("-" * 20)
        
        # Test valid IDs (10 digits)
        valid_ids = ["1234567890", "0987654321"]
        for id_num in valid_ids:
            result = assistant.collect_customer_id(id_num)
            data = json.loads(result)
            print(f"✅ {id_num}: {data.get('status', 'unknown')}")
            
        # Test invalid IDs
        invalid_ids = ["123456789", "12345678901", "abc1234567", "123-456-789"]
        for id_num in invalid_ids:
            result = assistant.collect_customer_id(id_num)
            data = json.loads(result)
            print(f"❌ {id_num}: {data.get('message', 'unknown error')}")
            
        print("\n📸 TESTING IMAGE UPLOAD FLOW:")
        print("-" * 25)
        
        # Test image upload instructions
        result = assistant.collect_customer_image()
        data = json.loads(result)
        print(f"📋 Image Upload Status: {data.get('status', 'unknown')}")
        print(f"📝 Message: {data.get('message', 'No message')}")
        
        # Test image verification
        result = assistant.verify_image_upload()
        data = json.loads(result)
        print(f"🔍 Image Verification: {data.get('image_status', 'unknown')}")
        
        print("\n✅ ALL VALIDATION TESTS COMPLETED!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_validations()
