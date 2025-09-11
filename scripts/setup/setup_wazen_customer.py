#!/usr/bin/env python
"""
Setup script for Wazen customer integration

This script creates:
1. Wazen company record in the system database
2. Wazen customer user account with appropriate permissions
3. Sample knowledge base content for testing
4. Proper company associations and permissions

Run this script after migrating the knowledge base models.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from company.models import Company
from product.models import KnowledgeCategory, KnowledgeArticle

User = get_user_model()


def create_wazen_company():
    """Create Wazen company record"""
    print("Creating Wazen company...")
    
    company, created = Company.objects.get_or_create(
        name='Wazen',
        defaults={
            'address': 'Wazen Business Center, Technology District',
            'phone': '+966-11-123-4567',
            'email': 'info@wazen.com',
            'website': 'https://www.wazen.com',
            'description': 'Leading customer support and business solutions provider'
        }
    )
    
    if created:
        print(f"✅ Created Wazen company: {company.name}")
    else:
        print(f"✅ Wazen company already exists: {company.name}")
    
    return company


def create_wazen_user(company):
    """Create Wazen customer user account"""
    print("Creating Wazen customer user...")
    
    username = 'wazen_user'
    email = 'user@wazen.com'
    password = 'wazen123'  # Change this in production
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': 'Wazen',
            'last_name': 'Customer',
            'is_customer': True,
            'is_staff': False,
            'is_superuser': False,
            'company': company
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Created Wazen user: {username} (password: {password})")
    else:
        # Update existing user to ensure proper settings
        user.is_customer = True
        user.company = company
        user.save()
        print(f"✅ Updated existing Wazen user: {username}")
    
    return user


def create_sample_knowledge_content(company):
    """Create sample knowledge base content for Wazen"""
    print("Creating sample knowledge base content...")
    
    # Create knowledge categories
    categories_data = [
        {
            'name': 'Services',
            'description': 'Information about Wazen services and offerings',
            'display_order': 1
        },
        {
            'name': 'Policies',
            'description': 'Company policies, terms and conditions',
            'display_order': 2
        },
        {
            'name': 'FAQ',
            'description': 'Frequently asked questions',
            'display_order': 3
        },
        {
            'name': 'Support',
            'description': 'Customer support information',
            'display_order': 4
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = KnowledgeCategory.objects.get_or_create(
            company=company,
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        if created:
            print(f"  ✅ Created category: {cat_data['name']}")
    
    # Create sample articles
    articles_data = [
        {
            'category': 'Services',
            'title': 'Customer Support Solutions',
            'content': '''Wazen provides comprehensive customer support solutions including:

• 24/7 multilingual customer service
• AI-powered chatbot integration
• Ticket management systems
• Customer satisfaction analytics
• Training and consultation services

Our solutions are designed to enhance customer experience and improve business efficiency.''',
            'article_type': 'service',
            'keywords': 'customer support, chatbot, multilingual, 24/7, analytics',
            'display_order': 1
        },
        {
            'category': 'Services',
            'title': 'Business Process Automation',
            'content': '''Transform your business operations with our automation solutions:

• Workflow automation and optimization
• Document processing and management
• Integration with existing systems
• Custom software development
• Process analysis and improvement

Reduce manual work and increase productivity with our proven automation frameworks.''',
            'article_type': 'service',
            'keywords': 'automation, workflow, integration, productivity, software',
            'display_order': 2
        },
        {
            'category': 'Policies',
            'title': 'Service Level Agreement (SLA)',
            'content': '''Our Service Level Agreement guarantees:

**Response Times:**
• Critical issues: 1 hour response
• High priority: 4 hours response
• Medium priority: 24 hours response
• Low priority: 72 hours response

**Availability:**
• 99.9% uptime guarantee
• Scheduled maintenance windows
• Disaster recovery procedures

**Support Coverage:**
• 24/7 technical support
• Dedicated account manager
• Regular performance reviews''',
            'article_type': 'policy',
            'keywords': 'SLA, response time, uptime, support, guarantee',
            'display_order': 1
        },
        {
            'category': 'FAQ',
            'title': 'How to Contact Support',
            'content': '''You can reach our support team through multiple channels:

**Phone Support:**
• Main line: +966-11-123-4567
• Emergency line: +966-11-123-4568
• Available 24/7

**Email Support:**
• General inquiries: support@wazen.com
• Technical issues: tech@wazen.com
• Billing questions: billing@wazen.com

**Online Support:**
• Live chat on our website
• Support portal: portal.wazen.com
• Knowledge base: help.wazen.com

**Business Hours:**
• Sunday - Thursday: 8:00 AM - 6:00 PM
• Friday - Saturday: Emergency support only''',
            'article_type': 'faq',
            'keywords': 'contact, support, phone, email, chat, hours',
            'display_order': 1
        },
        {
            'category': 'FAQ',
            'title': 'Billing and Payment Information',
            'content': '''Information about billing and payments:

**Payment Methods:**
• Bank transfer
• Credit card (Visa, Mastercard)
• Online payment portal
• Monthly invoicing available

**Billing Cycle:**
• Monthly billing on the 1st of each month
• Invoices sent via email
• 30-day payment terms
• Late payment fees may apply

**Payment Portal:**
• Access at billing.wazen.com
• View invoices and payment history
• Set up automatic payments
• Download receipts and statements''',
            'article_type': 'faq',
            'keywords': 'billing, payment, invoice, credit card, portal',
            'display_order': 2
        },
        {
            'category': 'Support',
            'title': 'Getting Started Guide',
            'content': '''Welcome to Wazen! Here's how to get started:

**Step 1: Account Setup**
• Complete your profile information
• Verify your email address
• Set up two-factor authentication

**Step 2: Service Configuration**
• Choose your service package
• Configure integration settings
• Set up user accounts and permissions

**Step 3: Training and Onboarding**
• Schedule training sessions
• Access online tutorials
• Connect with your account manager

**Step 4: Go Live**
• Conduct system testing
• Launch your services
• Monitor performance metrics

Need help? Contact your dedicated account manager or our support team.''',
            'article_type': 'procedure',
            'keywords': 'getting started, setup, configuration, training, onboarding',
            'display_order': 1
        }
    ]
    
    for article_data in articles_data:
        category = categories[article_data['category']]
        article_data['company'] = company
        article_data['category'] = category
        
        article, created = KnowledgeArticle.objects.get_or_create(
            company=company,
            title=article_data['title'],
            defaults=article_data
        )
        
        if created:
            print(f"  ✅ Created article: {article_data['title']}")
    
    print(f"✅ Knowledge base setup complete with {len(categories)} categories and {len(articles_data)} articles")


def main():
    """Main setup function"""
    print("🚀 Setting up Wazen customer integration...")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Create company
            company = create_wazen_company()
            
            # Create user
            user = create_wazen_user(company)
            
            # Create sample knowledge content
            create_sample_knowledge_content(company)
            
            print("=" * 60)
            print("✅ Wazen customer setup completed successfully!")
            print()
            print("📋 Setup Summary:")
            print(f"   Company: {company.name}")
            print(f"   User: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Password: wazen123")
            print(f"   Company ID: {company.id}")
            print()
            print("🎯 Next Steps:")
            print("   1. Login with the Wazen user credentials")
            print("   2. Test the hybrid AI assistant in the chat interface")
            print("   3. Try both database queries and knowledge base searches")
            print("   4. Add more knowledge content through Django admin")
            print()
            print("🔗 Access Points:")
            print("   • Chat Interface: http://127.0.0.1:8000/chat/")
            print("   • Django Admin: http://127.0.0.1:8000/admin/")
            print("   • Knowledge Management: Admin > Product > Knowledge Articles")
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
