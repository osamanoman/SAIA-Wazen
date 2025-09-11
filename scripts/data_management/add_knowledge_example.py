#!/usr/bin/env python
"""
Example script to add knowledge base content for Wazen
Run with: python manage.py shell < add_knowledge_example.py
"""

from company.models import Company
from product.models import KnowledgeCategory, KnowledgeArticle, FAQ

print("📚 ADDING NEW KNOWLEDGE BASE CONTENT FOR WAZEN")
print("=" * 55)

# Get Wazen company
wazen_company = Company.objects.get(name='Wazen')

# Example 1: Add a new knowledge category
new_category, created = KnowledgeCategory.objects.get_or_create(
    company=wazen_company,
    name='Product Features',
    defaults={
        'description': 'Information about Wazen platform features and capabilities',
        'display_order': 10,
        'is_active': True
    }
)

if created:
    print(f"✅ Created new category: {new_category.name}")
else:
    print(f"📋 Category already exists: {new_category.name}")

# Example 2: Add a new knowledge article
new_article, created = KnowledgeArticle.objects.get_or_create(
    company=wazen_company,
    title='How to Use AI Assistant',
    defaults={
        'category': new_category,
        'content': """
# How to Use Wazen AI Assistant

## Getting Started
The Wazen AI Assistant is your personal business intelligence companion that helps you:

- **Analyze your business data** from invoices, contacts, and transactions
- **Get insights** about your business performance
- **Search your database** for specific information
- **Generate reports** and summaries

## How to Access
1. **Login** to your Wazen account
2. **Look for the chat bubble** in the bottom-right corner
3. **Click the bubble** to start chatting with your AI assistant

## What You Can Ask
- "Show me all my invoices from this month"
- "How many customers do I have?"
- "What's my total revenue?"
- "Find contacts in Riyadh"
- "Give me a database overview"

## AI Tools Available
Your AI assistant has access to these tools:
- Invoice analysis and reporting
- Customer contact management
- Database overview and statistics
- Custom data searches
- Table descriptions and samples

## Tips for Better Results
- **Be specific** in your questions
- **Use clear language** (Arabic or English)
- **Ask follow-up questions** for more details
- **Request specific time periods** when relevant

## Support
If you need help with the AI assistant, contact our support team at 920003751.
        """,
        'article_type': 'procedure',
        'keywords': 'AI assistant, chat, business intelligence, data analysis, help',
        'locale': 'en',
        'is_active': True,
        'published': True,
        'display_order': 1
    }
)

if created:
    print(f"✅ Created new article: {new_article.title}")
else:
    print(f"📋 Article already exists: {new_article.title}")

# Example 3: Add a new FAQ
new_faq, created = FAQ.objects.get_or_create(
    company=wazen_company,
    question='How do I chat with the AI assistant about my business data?',
    defaults={
        'answer_md': """
To chat with your AI assistant about your business data:

1. **Login** to your Wazen account
2. **Find the chat bubble** in the bottom-right corner of the screen
3. **Click the bubble** to open the chat interface
4. **Type your question** in Arabic or English

## Example Questions:
- "Show me my recent invoices"
- "How many customers do I have?"
- "What's in my database?"
- "Find all paid invoices"

## What the AI Can Access:
- Your invoice data
- Customer contact information  
- Business transaction records
- Database statistics and overviews

The AI assistant only has access to **your company's data** and cannot see other customers' information.
        """,
        'tags': ['AI', 'assistant', 'chat', 'business data', 'help'],
        'locale': 'en',
        'is_active': True,
        'published': True,
        'display_order': 1
    }
)

if created:
    print(f"✅ Created new FAQ: {new_faq.question}")
else:
    print(f"📋 FAQ already exists: {new_faq.question}")

# Show summary
print(f"\n🎯 KNOWLEDGE BASE SUMMARY:")
categories = KnowledgeCategory.objects.filter(company=wazen_company)
articles = KnowledgeArticle.objects.filter(company=wazen_company, is_active=True)
faqs = FAQ.objects.filter(company=wazen_company, is_active=True)

print(f"   📂 Categories: {categories.count()}")
print(f"   📄 Articles: {articles.count()}")
print(f"   ❓ FAQs: {faqs.count()}")

print(f"\n✅ Knowledge base content added successfully!")
print(f"   Customers can now find this information through:")
print(f"   - AI assistant chat")
print(f"   - Admin interface browsing")
print(f"   - Full-text search")
