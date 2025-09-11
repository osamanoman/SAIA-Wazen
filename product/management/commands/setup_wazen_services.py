"""
Management command to set up correct Wazen services based on wazen-data.md specifications.
Wazen offers exactly 2 vehicle insurance services as defined in their business documentation.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from company.models import Company
from product.models import Product


class Command(BaseCommand):
    help = 'Set up correct Wazen services based on wazen-data.md specifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up correct Wazen services from wazen-data.md...'))

        try:
            # Get Wazen company
            wazen_company = Company.objects.get(name='Wazen')
            self.stdout.write(f'Found Wazen company: {wazen_company.name}')

            # Create correct services based on wazen-data.md
            # Wazen offers exactly 2 vehicle insurance services
            services_data = [
                {
                    'name': 'تأمين المركبات ضد الغير',
                    'price': 500.00,
                    'service_description': '''التأمين الإلزامي للمركبات - الحد الأدنى من التغطية المطلوبة قانونياً.

ما يشمله التأمين:
• تغطية مسؤوليتك القانونية تجاه الأضرار الجسدية أو المادية التي قد تسببها لطرف ثالث (أفراد أو ممتلكات)
• الحماية من المطالبات المالية الناتجة عن الحوادث المرورية حتى مبلغ 10 مليون ريال

لماذا تختاره:
• لحمايتك من المسؤولية المدنية تجاه الآخرين عند وقوع حادث سير للمركبة
• متطلب نظامي من قبل الجهات المعنية يقدم الحد الأدنى من التغطية المطلوبة

ملاحظة: هذا التأمين لا يغطي أضرار مركبتك أو إصابتك الشخصية.''',
                    'is_service_orderable': True,
                    'requires_customer_info': True
                },
                {
                    'name': 'التأمين الشامل',
                    'price': 1500.00,
                    'service_description': '''الحماية الكاملة لمركبتك وللطرف الثالث - التغطية الأشمل والأكثر حماية.

ما يشمله التأمين:
• تغطية أضرار مركبتك الناتجة عن الحوادث، والحرائق، والسرقة، والكوارث الطبيعية (مثل الفيضانات أو العواصف)
• تغطية مسؤوليتك تجاه الأضرار التي تلحق بالغير (كما في التأمين ضد الغير)
• تغطيات اختيارية: تمديد التغطية لدول الخليج، تغطية الزجاج، وغيرها

لماذا تختاره:
• حماية شاملة لمركبتك واستثمارك من معظم المخاطر
• مرن مع إمكانية إضافة تغطيات اختيارية تناسب احتياجاتك الخاصة
• مثالي للأشخاص الذين يرغبون في تغطية أضرار مركباتهم وحمايتهم من المسؤولية تجاه الغير وللمركبات الجديدة أو ذات القيمة العالية''',
                    'is_service_orderable': True,
                    'requires_customer_info': True
                }
            ]

            created_count = 0
            updated_count = 0

            for service_data in services_data:
                service, created = Product.objects.get_or_create(
                    name=service_data['name'],
                    company=wazen_company,
                    defaults={
                        'price': service_data['price'],
                        'type': 'service',
                        'quantity': 999,  # Services don't have quantity limits
                        'expiration': timezone.now().date().replace(year=2025),
                        'service_description': service_data['service_description'],
                        'is_service_orderable': service_data['is_service_orderable'],
                        'requires_customer_info': service_data['requires_customer_info']
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created service: {service.name}')
                    )
                else:
                    # Update existing service
                    service.price = service_data['price']
                    service.type = 'service'
                    service.service_description = service_data['service_description']
                    service.is_service_orderable = service_data['is_service_orderable']
                    service.requires_customer_info = service_data['requires_customer_info']
                    service.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Updated existing service: {service.name}')
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Setup complete! Created {created_count} new services, updated {updated_count} existing services.'
                )
            )

            # Display summary
            total_services = Product.objects.filter(
                company=wazen_company,
                type='service',
                is_service_orderable=True
            ).count()

            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 Total orderable services for Wazen: {total_services}'
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ Services now match wazen-data.md specifications:'
                )
            )
            self.stdout.write('   1. تأمين المركبات ضد الغير (Third Party Insurance)')
            self.stdout.write('   2. التأمين الشامل (Comprehensive Insurance)')

        except Company.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Wazen company not found. Please create the Wazen company first.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up services: {e}')
            )
