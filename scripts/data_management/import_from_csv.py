#!/usr/bin/env python
"""
Script to import knowledge base content from CSV file
CSV format: title,content,category,article_type,keywords
"""

import csv
from company.models import Company
from product.models import KnowledgeCategory, KnowledgeArticle
from django.contrib.auth import get_user_model

def import_from_csv(csv_file_path):
    """Import knowledge articles from CSV file"""
    
    # Setup
    wazen_company = Company.objects.get(name='Wazen')
    User = get_user_model()
    admin_user = User.objects.get(username='admin')
    
    # Get categories
    faq_category, _ = KnowledgeCategory.objects.get_or_create(
        company=wazen_company,
        name='FAQ',
        defaults={'description': 'Frequently Asked Questions'}
    )
    
    company_category, _ = KnowledgeCategory.objects.get_or_create(
        company=wazen_company,
        name='Company Information',
        defaults={'description': 'General company information'}
    )
    
    category_map = {
        'FAQ': faq_category,
        'Company Information': company_category,
        'faq': faq_category,
        'company': company_category
    }
    
    added_count = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            title = row['title'].strip()
            content = row['content'].strip()
            category_name = row['category'].strip()
            article_type = row['article_type'].strip()
            keywords = row['keywords'].strip()
            
            # Get category
            category = category_map.get(category_name, faq_category)
            
            # Check if already exists
            existing = KnowledgeArticle.objects.filter(
                company=wazen_company,
                title=title
            ).first()
            
            if not existing:
                KnowledgeArticle.objects.create(
                    company=wazen_company,
                    category=category,
                    title=title,
                    content=content,
                    article_type=article_type,
                    keywords=keywords
                )
                added_count += 1
                print(f'✅ Added: {title[:50]}...')
            else:
                print(f'⚠️  Exists: {title[:50]}...')
    
    print(f'\n📊 Successfully imported {added_count} articles from CSV!')

# Example usage:
# import_from_csv('knowledge_articles.csv')
