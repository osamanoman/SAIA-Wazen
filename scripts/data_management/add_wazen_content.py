#!/usr/bin/env python
"""
Script to add more content to Wazen knowledge base

Usage:
1. Modify the content in this script
2. Run: python manage.py shell < add_wazen_content.py
"""

from company.models import Company
from product.models import KnowledgeCategory, KnowledgeArticle

print('📝 Adding more content to Wazen knowledge base...')

# Get Wazen company
try:
    company = Company.objects.get(name='Wazen')
    print(f'✅ Found Wazen company: {company.name}')
except Company.DoesNotExist:
    print('❌ Wazen company not found!')
    exit()

# Get or create categories
categories_data = [
    {
        'name': 'Claims Process',
        'description': 'How to file and track insurance claims',
        'display_order': 6
    },
    {
        'name': 'Payment Methods',
        'description': 'Available payment options and billing information',
        'display_order': 7
    },
    {
        'name': 'Technical Support',
        'description': 'Technical help and troubleshooting',
        'display_order': 8
    },
    {
        'name': 'Account Management',
        'description': 'Managing your Wazen account and profile',
        'display_order': 9
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
        print(f'  ✅ Created category: {cat_data["name"]}')
    else:
        print(f'  ℹ️  Category exists: {cat_data["name"]}')

# Add new articles
articles_data = [
    {
        'category': 'Claims Process',
        'title': 'How to File an Insurance Claim',
        'content': '''**How to File an Insurance Claim**

## Step-by-Step Process

### 1. Immediate Actions After an Incident
• Ensure safety of all parties involved
• Contact emergency services if needed (911)
• Document the scene with photos
• Exchange information with other parties
• Contact Wazen claims department immediately

### 2. Required Information
• Policy number
• Date, time, and location of incident
• Description of what happened
• Photos of damage
• Police report number (if applicable)
• Contact information of all parties involved

### 3. Filing Your Claim
• **Online**: Visit www.wazen.com and login to your account
• **Phone**: Call our claims hotline at 920003751
• **Mobile App**: Use the Wazen mobile app
• **In Person**: Visit any Wazen service center

### 4. Claim Processing Timeline
• **Initial Review**: 24-48 hours
• **Investigation**: 3-7 business days
• **Settlement**: 7-14 business days after approval

### 5. Required Documents
• Completed claim form
• Copy of driving license
• Copy of vehicle registration
• Police report (if applicable)
• Repair estimates
• Medical reports (for injury claims)

**Need Help?** Contact our claims specialists at 920003751 or visit www.wazen.com/claims''',
        'article_type': 'procedure',
        'keywords': 'claims, insurance claim, file claim, accident, damage, process, timeline',
        'display_order': 1
    },
    {
        'category': 'Payment Methods',
        'title': 'Available Payment Options',
        'content': '''**Available Payment Options**

## Online Payment Methods

### Credit/Debit Cards
• **Visa** - All types accepted
• **Mastercard** - All types accepted
• **American Express** - Selected cards
• **Mada** - Saudi local cards

### Digital Wallets
• **Apple Pay** - iPhone and iPad users
• **Samsung Pay** - Samsung device users
• **STC Pay** - Saudi Telecom digital wallet
• **Urpay** - Local digital payment solution

### Bank Transfer
• **SADAD** - Saudi Arabia's national payment system
• **Direct Bank Transfer** - From any Saudi bank
• **Standing Order** - Automatic monthly payments

## Payment Security
• **SSL Encryption** - All transactions secured
• **PCI Compliance** - Industry standard security
• **3D Secure** - Additional verification layer
• **Fraud Protection** - Real-time monitoring

## Payment Support
• **24/7 Payment Support**: 920003751
• **Online Help**: www.wazen.com/payment-help
• **Live Chat**: Available during business hours

## Billing Cycle
• **Monthly Billing**: 1st of each month
• **Payment Due**: 30 days from invoice date
• **Late Fees**: Applied after 30 days
• **Grace Period**: 5 days before late fees

**Questions about payments?** Contact our billing department at billing@wazen.com''',
        'article_type': 'service',
        'keywords': 'payment, billing, credit card, mada, apple pay, bank transfer, sadad',
        'display_order': 1
    },
    {
        'category': 'Technical Support',
        'title': 'Website and App Troubleshooting',
        'content': '''**Website and App Troubleshooting**

## Common Issues and Solutions

### Website Not Loading
**Problem**: Wazen website won't open or loads slowly
**Solutions**:
• Clear your browser cache and cookies
• Try a different browser (Chrome, Safari, Firefox)
• Check your internet connection
• Disable browser extensions temporarily
• Try incognito/private browsing mode

### Login Problems
**Problem**: Cannot login to your account
**Solutions**:
• Verify your username and password
• Use "Forgot Password" to reset
• Clear browser cache
• Check if Caps Lock is on
• Try logging in from a different device

### Mobile App Issues
**Problem**: Wazen app crashes or won't work
**Solutions**:
• Update the app to latest version
• Restart your phone
• Clear app cache (Android) or reinstall (iOS)
• Check available storage space
• Ensure stable internet connection

### Payment Failures
**Problem**: Payment not processing
**Solutions**:
• Verify card details are correct
• Check card expiry date
• Ensure sufficient funds/credit limit
• Try a different payment method
• Contact your bank if card is blocked

### Document Upload Issues
**Problem**: Cannot upload documents
**Solutions**:
• Check file size (max 5MB per file)
• Use supported formats: PDF, JPG, PNG
• Ensure good image quality
• Try uploading one file at a time
• Use a stable internet connection

## Browser Requirements
• **Chrome**: Version 90 or newer
• **Safari**: Version 14 or newer
• **Firefox**: Version 88 or newer
• **Edge**: Version 90 or newer

## Mobile App Requirements
• **iOS**: Version 13.0 or newer
• **Android**: Version 8.0 or newer

**Still having issues?** Contact technical support:
• **Phone**: 920003751
• **Email**: tech@wazen.com
• **Live Chat**: Available 8 AM - 11 PM''',
        'article_type': 'faq',
        'keywords': 'technical support, troubleshooting, website, app, login, payment, upload',
        'display_order': 1
    },
    {
        'category': 'Account Management',
        'title': 'Managing Your Wazen Account',
        'content': '''**Managing Your Wazen Account**

## Account Setup and Profile

### Creating Your Account
• Visit www.wazen.com and click "Register"
• Provide required information (ID, phone, email)
• Verify your phone number with SMS code
• Set a strong password
• Complete your profile information

### Profile Information
**Personal Details**:
• Full name (as per ID)
• National ID or Iqama number
• Date of birth
• Phone number
• Email address
• National address

**Vehicle Information**:
• Vehicle registration details
• License plate number
• Vehicle identification number (VIN)
• Vehicle make, model, and year

### Account Security

**Password Requirements**:
• Minimum 8 characters
• Include uppercase and lowercase letters
• Include at least one number
• Include at least one special character

**Two-Factor Authentication**:
• Enable SMS verification
• Use authenticator app (optional)
• Backup codes for recovery

### Managing Your Policies

**View Policies**:
• Login to your account
• Go to "My Policies" section
• View active, expired, and upcoming policies
• Download policy documents

**Policy Renewal**:
• Automatic renewal reminders
• Online renewal process
• Compare quotes before renewal
• Update vehicle or personal information

### Account Settings

**Communication Preferences**:
• Email notifications
• SMS alerts
• Language preference (Arabic/English)
• Marketing communications opt-in/out

**Privacy Settings**:
• Data sharing preferences
• Third-party access permissions
• Account visibility settings

### Account Support
• **Self-Service**: Most tasks available online
• **Phone Support**: 920003751
• **Email Support**: support@wazen.com
• **Live Chat**: Business hours only

**Account locked or compromised?** Contact security team immediately at security@wazen.com''',
        'article_type': 'procedure',
        'keywords': 'account, profile, security, password, policies, settings, privacy',
        'display_order': 1
    }
]

# Create articles
created_count = 0
for article_data in articles_data:
    category = categories[article_data['category']]
    article, created = KnowledgeArticle.objects.get_or_create(
        company=company,
        title=article_data['title'],
        defaults={
            'category': category,
            'content': article_data['content'],
            'article_type': article_data['article_type'],
            'keywords': article_data['keywords'],
            'display_order': article_data['display_order']
        }
    )
    
    if created:
        print(f'  ✅ Created article: {article_data["title"]}')
        created_count += 1
    else:
        print(f'  ℹ️  Article exists: {article_data["title"]}')

print(f'\n✅ Content addition complete!')
print(f'📊 Summary:')
print(f'   • Categories: {len(categories)} total')
print(f'   • New Articles: {created_count}')
print(f'   • Company: {company.name}')
print(f'\n🎯 Next steps:')
print(f'   1. Test the new content in the chat interface')
print(f'   2. Login as wazen_user and try queries like:')
print(f'      - "How do I file an insurance claim?"')
print(f'      - "What payment methods do you accept?"')
print(f'      - "I need technical support"')
print(f'      - "How do I manage my account?"')
