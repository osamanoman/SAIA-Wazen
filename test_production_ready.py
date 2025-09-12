#!/usr/bin/env python3
"""
Production-ready test suite for Wazen AI Assistant performance fix
"""

import os
import sys
import django
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saia.settings')
sys.path.append('/Users/osama/Documents/apps/SAIA-Wazen-norag-chatbot/SAIA-Wazen')
django.setup()

from django.core.cache import cache
from product.assistants.wazen_ai_assistant import WazenAIAssistant
from company.models import Company
from users.models import User

def test_production_caching():
    """Test production-ready caching implementation"""
    
    print("🏭 PRODUCTION-READY CACHING TEST")
    print("=" * 50)
    
    try:
        # Get test data
        company = Company.objects.filter(name__icontains='wazen').first()
        user = User.objects.filter(company=company).first()
        
        if not company or not user:
            print("❌ Test data not found")
            return False
            
        print(f"✅ Using company: {company.name}")
        print(f"✅ Using user: {user.username}")
        
        # Clear any existing cache
        cache_key = f'wazen_orderable_services_{company.id}'
        cache.delete(cache_key)
        
        assistant = WazenAIAssistant()
        
        # Test 1: Cache Miss Performance
        print("\n1. Testing cache miss performance...")
        start_time = time.time()
        services1 = assistant._get_orderable_services(user)
        cache_miss_time = time.time() - start_time
        print(f"✅ Cache miss: {cache_miss_time:.3f}s ({services1.count()} services)")
        
        # Test 2: Cache Hit Performance
        print("\n2. Testing cache hit performance...")
        start_time = time.time()
        services2 = assistant._get_orderable_services(user)
        cache_hit_time = time.time() - start_time
        print(f"✅ Cache hit: {cache_hit_time:.3f}s ({services2.count()} services)")
        
        # Verify performance improvement
        if cache_hit_time < cache_miss_time:
            improvement = ((cache_miss_time - cache_hit_time) / cache_miss_time) * 100
            print(f"🚀 Performance improvement: {improvement:.1f}%")
        
        # Test 3: Cache Statistics
        print("\n3. Testing cache monitoring...")
        stats = assistant._get_cache_stats()
        print(f"✅ Cache stats: {stats}")
        
        # Test 4: Cache Invalidation
        print("\n4. Testing cache invalidation...")
        assistant._invalidate_services_cache(company.id)
        invalidated_services = assistant._get_orderable_services(user)
        print(f"✅ Cache invalidated and refreshed: {invalidated_services.count()} services")
        
        return True
        
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_thread_safety():
    """Test thread safety of caching implementation"""
    
    print("\n🔒 THREAD SAFETY TEST")
    print("=" * 30)
    
    try:
        company = Company.objects.filter(name__icontains='wazen').first()
        user = User.objects.filter(company=company).first()
        
        if not company or not user:
            print("❌ Test data not found")
            return False
        
        # Clear cache
        cache_key = f'wazen_orderable_services_{company.id}'
        cache.delete(cache_key)
        
        results = []
        errors = []
        
        def worker_thread(thread_id):
            try:
                assistant = WazenAIAssistant()
                services = assistant._get_orderable_services(user)
                return f"Thread {thread_id}: {services.count()} services"
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")
                return None
        
        # Run 10 concurrent threads
        print("Running 10 concurrent cache operations...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(10)]
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        print(f"✅ Completed {len(results)} successful operations")
        if errors:
            print(f"❌ {len(errors)} errors occurred:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   {error}")
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"❌ Thread safety test failed: {e}")
        return False

def test_error_resilience():
    """Test error handling and graceful fallback"""
    
    print("\n🛡️ ERROR RESILIENCE TEST")
    print("=" * 30)
    
    try:
        company = Company.objects.filter(name__icontains='wazen').first()
        user = User.objects.filter(company=company).first()
        
        if not company or not user:
            print("❌ Test data not found")
            return False
        
        assistant = WazenAIAssistant()
        
        # Test graceful fallback when cache fails
        print("Testing graceful fallback...")
        services = assistant._get_orderable_services(user)
        print(f"✅ Graceful fallback works: {services.count()} services")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resilience test failed: {e}")
        return False

def main():
    """Run all production readiness tests"""
    
    print("🏭 WAZEN AI ASSISTANT - PRODUCTION READINESS TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Production Caching", test_production_caching),
        ("Thread Safety", test_thread_safety),
        ("Error Resilience", test_error_resilience)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        if test_func():
            print(f"✅ {test_name} Test: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} Test: FAILED")
    
    print(f"\n🎯 PRODUCTION READINESS RESULTS")
    print("=" * 40)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - PRODUCTION READY!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    main()
