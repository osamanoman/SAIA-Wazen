"""
Management command to set up sample Wazen services for testing the service ordering system.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from company.models import Company
from product.models import Product


class Command(BaseCommand):
    help = 'Set up sample Wazen services for testing service ordering'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Wazen services...'))

        try:
            # Get Wazen company
            wazen_company = Company.objects.get(name='Wazen')
            self.stdout.write(f'Found Wazen company: {wazen_company.name}')

            # Create sample services
            services_data = [
                {
                    'name': 'تأمين السيارات',
                    'price': 1200.00,
                    'service_description': 'تأمين شامل للسيارات يغطي جميع المخاطر والحوادث. يشمل التأمين ضد الحوادث والسرقة والحريق والكوارث الطبيعية.',
                    'is_service_orderable': True,
                    'requires_customer_info': True
                },
                {
                    'name': 'تأمين المنزل',
                    'price': 800.00,
                    'service_description': 'تأمين شامل للمنزل والممتلكات. يغطي الحرائق والسرقة والأضرار الناتجة عن الكوارث الطبيعية.',
                    'is_service_orderable': True,
                    'requires_customer_info': True
                },
                {
                    'name': 'تأمين صحي',
                    'price': 2500.00,
                    'service_description': 'تأمين صحي شامل يغطي العلاج في المستشفيات والعيادات. يشمل الفحوصات الدورية والعمليات الجراحية.',
                    'is_service_orderable': True,
                    'requires_customer_info': True
                },
                {
                    'name': 'تأمين السفر',
                    'price': 300.00,
                    'service_description': 'تأمين شامل للسفر يغطي الطوارئ الطبية وإلغاء الرحلات وفقدان الأمتعة.',
                    'is_service_orderable': True,
                    'requires_customer_info': True
                },
                {
                    'name': 'استشارة تأمينية',
                    'price': 150.00,
                    'service_description': 'استشارة مجانية مع خبراء التأمين لتحديد أفضل خطة تأمينية تناسب احتياجاتك.',
                    'is_service_orderable': True,
                    'requires_customer_info': False
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
