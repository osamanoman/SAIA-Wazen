#!/usr/bin/env python
"""
Script to manually add knowledge base content
Run this with: python manage.py shell < add_knowledge_content.py
"""

from company.models import Company
from product.models import KnowledgeCategory, KnowledgeArticle
from django.contrib.auth import get_user_model

# Setup
print("🔧 Setting up knowledge base content...")
wazen_company = Company.objects.get(name='Wazen')
User = get_user_model()
admin_user = User.objects.get(username='admin')

# Get or create categories
faq_category, created = KnowledgeCategory.objects.get_or_create(
    company=wazen_company,
    name='FAQ',
    defaults={'description': 'Frequently Asked Questions'}
)

company_category, created = KnowledgeCategory.objects.get_or_create(
    company=wazen_company,
    name='Company Information',
    defaults={'description': 'General company information'}
)

# Define articles to add
articles_to_add = [
    {
        'title': 'لم يصلني رمز التحقق عبر رسالة نصية للجوال؟',
        'content': 'سيتم إرسال رمز التحقق خلال الجوال بحد أقصى (4) دقائق وفي حال لم تصل الرسالة يرجى التأكد من الرقم المستخدم أعلى خانة رمز التحقق، إذا كان الرقم صحيح يرجى الضغط على زر إعادة الإرسال، إذا لم يصلك الرمز خلال عدة محاولات، يرجى التواصل مع خدمة العملاء.',
        'category': faq_category,
        'article_type': 'faq',
        'keywords': 'رمز,تحقق,رسالة,نصية,جوال,تسجيل'
    },
    {
        'title': 'كيف أطبع وثيقة التأمين؟',
        'content': 'يمكنك طباعة وثيقة التأمين من خلال: 1) الدخول لحسابك في موقع وازن 2) الضغط على "حسابي" 3) اختيار "وثائق سارية المفعول" 4) الضغط على الوثيقة المطلوبة 5) اختيار "طباعة". ننصح بطباعة الوثيقة والاحتفاظ بها في المركبة دوماً.',
        'category': faq_category,
        'article_type': 'faq',
        'keywords': 'طباعة,وثيقة,تأمين,حساب,احتفاظ'
    },
    {
        'title': 'من هي شركة وازن؟',
        'content': 'وازن هي منصة رقمية متخصصة في تقديم خدمات التأمين بأسلوب مبسط وسهل. نهدف إلى تمكين الأفراد والشركات من إدارة وثائقهم ومطالباتهم بكل شفافية وسهولة. وازن وسيط تأمين إلكتروني مرخص من قبل هيئة التأمين.',
        'category': company_category,
        'article_type': 'general',
        'keywords': 'وازن,منصة,رقمية,تأمين,مرخص,هيئة,شركة'
    },
    {
        'title': 'ما هو الرقم التسلسلي للمركبة وأين يمكن إيجاده؟',
        'content': 'الرقم التسلسلي للمركبة هو الرقم الموجود في أسفل بطاقة "رخصة السير" للمركبة (الاستمارة). يمكن العثور عليه في الجزء السفلي من استمارة المركبة.',
        'category': faq_category,
        'article_type': 'faq',
        'keywords': 'رقم,تسلسلي,مركبة,هيكل,استمارة,رخصة,سير'
    },
    {
        'title': 'كيف ألغي وثيقة التأمين؟',
        'content': 'لا يمكن إلغاء وثيقة التأمين عن طريق موقع وازن، ويلزم مراجعة شركة التأمين المعنية للقيام بذلك. خدمة العملاء في وازن تساعدك في معرفة الإجراءات الواجب اتباعها عند الحاجة لإلغاء الوثيقة.',
        'category': faq_category,
        'article_type': 'faq',
        'keywords': 'إلغاء,الغي,وثيقة,تأمين,شركة,إجراءات'
    }
]

# Add articles
added_count = 0
for article_data in articles_to_add:
    # Check if already exists
    existing = KnowledgeArticle.objects.filter(
        company=wazen_company,
        title=article_data['title']
    ).first()
    
    if not existing:
        KnowledgeArticle.objects.create(
            company=wazen_company,
            category=article_data['category'],
            title=article_data['title'],
            content=article_data['content'],
            article_type=article_data['article_type'],
            keywords=article_data['keywords']
        )
        added_count += 1
        print(f'✅ Added: {article_data["title"][:50]}...')
    else:
        print(f'⚠️  Already exists: {article_data["title"][:50]}...')

print(f'\n📊 Successfully added {added_count} new articles!')
print('🎉 Knowledge base content updated!')
