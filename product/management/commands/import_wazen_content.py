"""
Management command to import Wazen content following the guide recommendations
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from product.models import KnowledgeCategory, KnowledgeArticle, FAQ
from company.models import Company


class Command(BaseCommand):
    help = 'Import Wazen content into the enhanced knowledge base structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company-id',
            type=int,
            required=True,
            help='Company ID to import content for'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )

    def handle(self, *args, **options):
        company_id = options['company_id']
        dry_run = options['dry_run']
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Company with ID {company_id} does not exist')
            )
            return

        self.stdout.write(f'Importing content for: {company.name}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))

        # Create categories
        categories_data = [
            {
                'name': 'عروض التأمين',
                'description': 'معلومات حول عروض التأمين المختلفة',
                'slug': 'insurance-offerings'
            },
            {
                'name': 'عن وازن',
                'description': 'معلومات عن الشركة ورؤيتها',
                'slug': 'about-wazen'
            },
            {
                'name': 'السياسات والشروط',
                'description': 'السياسات القانونية والشروط والأحكام',
                'slug': 'policies-terms'
            },
            {
                'name': 'الخصوصية',
                'description': 'سياسة الخصوصية وحماية البيانات',
                'slug': 'privacy'
            },
            {
                'name': 'الأسئلة الشائعة',
                'description': 'الأسئلة المتكررة وإجاباتها',
                'slug': 'faqs'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            if not dry_run:
                category, created = KnowledgeCategory.objects.get_or_create(
                    company=company,
                    name=cat_data['name'],
                    defaults={
                        'description': cat_data['description'],
                        'display_order': len(categories) + 1
                    }
                )
                categories[cat_data['slug']] = category
                status = 'Created' if created else 'Exists'
            else:
                status = 'Would create'
            
            self.stdout.write(f'  {status}: {cat_data["name"]}')

        # Insurance offerings articles
        insurance_articles = [
            {
                'title': 'تأمين المركبات ضد الغير – التأمين الإلزامي',
                'slug': 'vehicles-insurance-third-party',
                'category': 'insurance-offerings',
                'article_type': 'service',
                'content_md': '''## ما يشمله التأمين

- تغطية مسؤوليتك القانونية تجاه الأضرار الجسدية أو المادية للطرف الثالث
- الحماية من المطالبات المالية الناتجة عن الحوادث المرورية
- تغطية تكاليف العلاج الطبي للمصابين من الطرف الثالث
- تغطية أضرار ممتلكات الطرف الثالث

## لماذا تختاره

- **حماية قانونية**: حماية من المسؤولية المدنية تجاه الآخرين عند وقوع حادث
- **متطلب نظامي**: يحقق الحد الأدنى من التغطية المطلوبة قانونياً
- **سعر مناسب**: الخيار الأكثر اقتصادية للحصول على التأمين الإلزامي
- **سهولة الإجراءات**: عملية شراء مبسطة وسريعة

## المستندات المطلوبة

- صورة من رخصة القيادة سارية المفعول
- صورة من استمارة المركبة (الملكية)
- صورة من الهوية الوطنية أو الإقامة
- شهادة الفحص الدوري للمركبة (إن وجدت)''',
                'keywords': 'تأمين ضد الغير، التأمين الإلزامي، مركبات، حوادث، مسؤولية مدنية',
                'tags': ['مركبات', 'تأمين إلزامي', 'ضد الغير', 'حوادث']
            },
            {
                'title': 'التأمين الشامل – حماية مركبتك والطرف الثالث',
                'slug': 'vehicles-insurance-comprehensive',
                'category': 'insurance-offerings',
                'article_type': 'service',
                'content_md': '''## ما يشمله التأمين

- **أضرار مركبتك**: تغطية شاملة لأضرار مركبتك نتيجة الحوادث والحرائق والسرقة والكوارث الطبيعية
- **مسؤوليتك تجاه الغير**: تغطية كاملة للأضرار التي قد تلحق بالطرف الثالث
- **تغطيات اختيارية**: إمكانية إضافة تمديد الخليج، تأمين الزجاج، المساعدة على الطريق
- **قطع الغيار**: تغطية قطع الغيار الأصلية أو المعتمدة

## لماذا تختاره

- **حماية شاملة**: تغطية معظم المخاطر التي قد تتعرض لها مركبتك
- **مرونة في التغطية**: إمكانية إضافة تغطيات تناسب احتياجاتك الخاصة
- **مثالي للمركبات الجديدة**: الخيار الأفضل للمركبات الجديدة أو ذات القيمة العالية
- **راحة البال**: حماية شاملة تمنحك الثقة أثناء القيادة

## التغطيات الاختيارية

- **تمديد الخليج**: تغطية إضافية للسفر في دول الخليج
- **تأمين الزجاج**: تغطية خاصة لزجاج المركبة
- **المساعدة على الطريق**: خدمة الطوارئ والمساعدة الفنية
- **السائق الشخصي**: تغطية إضافية للسائق الشخصي''',
                'keywords': 'التأمين الشامل، مركبات، حماية شاملة، حوادث، سرقة، حريق',
                'tags': ['مركبات', 'تأمين شامل', 'حماية كاملة', 'تغطيات اختيارية']
            }
        ]

        # Import articles
        for article_data in insurance_articles:
            if not dry_run:
                category = categories[article_data['category']]
                article, created = KnowledgeArticle.objects.get_or_create(
                    company=company,
                    title=article_data['title'],
                    defaults={
                        'category': category,
                        'slug': article_data['slug'],
                        'content_md': article_data['content_md'],
                        'content': article_data['content_md'],  # Fallback
                        'article_type': article_data['article_type'],
                        'keywords': article_data['keywords'],
                        'tags': article_data['tags'],
                        'locale': 'ar',
                        'published': True,
                        'is_active': True
                    }
                )
                status = 'Created' if created else 'Updated'
                if not created:
                    # Update existing article
                    article.content_md = article_data['content_md']
                    article.content = article_data['content_md']
                    article.keywords = article_data['keywords']
                    article.tags = article_data['tags']
                    article.save()
            else:
                status = 'Would create'
            
            self.stdout.write(f'  {status}: {article_data["title"][:50]}...')

        # Sample FAQs
        faqs_data = [
            {
                'question': 'ما الفرق بين تأمين ضد الغير والتأمين الشامل؟',
                'answer_md': '''تأمين ضد الغير يغطي مسؤوليتك تجاه الغير فقط ولا يغطي أضرار مركبتك.

**التأمين الشامل** يغطي:
- أضرار مركبتك **بالإضافة** إلى مسؤوليتك تجاه الغير
- الحريق والسرقة والكوارث الطبيعية
- إمكانية إضافة تغطيات اختيارية

**الخلاصة**: التأمين الشامل يوفر حماية أكبر ولكن بتكلفة أعلى.''',
                'tags': ['مركبات', 'تغطية', 'سعر', 'مقارنة']
            },
            {
                'question': 'كيف أحصل على عرض سعر للتأمين؟',
                'answer_md': '''يمكنك الحصول على عرض سعر بسهولة من خلال:

1. **الموقع الإلكتروني**: ادخل بيانات مركبتك واحصل على عرض فوري
2. **التطبيق**: حمل تطبيق وازن واحصل على عروض متعددة
3. **خدمة العملاء**: اتصل بنا على الرقم المجاني

**المستندات المطلوبة**:
- رخصة القيادة
- استمارة المركبة
- الهوية الوطنية''',
                'tags': ['عرض سعر', 'شراء', 'مستندات', 'خدمة عملاء']
            }
        ]

        # Import FAQs
        for faq_data in faqs_data:
            if not dry_run:
                faq, created = FAQ.objects.get_or_create(
                    company=company,
                    question=faq_data['question'],
                    defaults={
                        'answer_md': faq_data['answer_md'],
                        'tags': faq_data['tags'],
                        'locale': 'ar',
                        'published': True,
                        'is_active': True
                    }
                )
                status = 'Created' if created else 'Updated'
                if not created:
                    faq.answer_md = faq_data['answer_md']
                    faq.tags = faq_data['tags']
                    faq.save()
            else:
                status = 'Would create'
            
            self.stdout.write(f'  {status}: {faq_data["question"][:50]}...')

        self.stdout.write(
            self.style.SUCCESS(f'✅ Content import completed for {company.name}')
        )
