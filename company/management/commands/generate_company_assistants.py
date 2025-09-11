"""
Django management command to generate AI assistants for existing companies.

Usage:
    python manage.py generate_company_assistants
    python manage.py generate_company_assistants --company-id 1
    python manage.py generate_company_assistants --company-name "Otek"
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from company.models import Company
from company.signals import generate_assistant_for_existing_company


class Command(BaseCommand):
    help = 'Generate AI assistants for existing companies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company-id',
            type=int,
            help='Generate assistant for specific company by ID',
        )
        parser.add_argument(
            '--company-name',
            type=str,
            help='Generate assistant for specific company by name',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if assistant already exists',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating files',
        )

    def handle(self, *args, **options):
        company_id = options.get('company_id')
        company_name = options.get('company_name')
        force = options.get('force', False)
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No files will be created')
            )

        try:
            # Determine which companies to process
            if company_id:
                companies = Company.objects.filter(id=company_id)
                if not companies.exists():
                    raise CommandError(f'Company with ID {company_id} does not exist')
            elif company_name:
                companies = Company.objects.filter(name__icontains=company_name)
                if not companies.exists():
                    raise CommandError(f'No companies found matching name "{company_name}"')
            else:
                companies = Company.objects.all()

            self.stdout.write(f'Processing {companies.count()} companies...\n')

            success_count = 0
            skip_count = 0
            error_count = 0

            for company in companies:
                self.stdout.write(f'Processing company: {company.name}')

                # Check if assistant already exists
                if not force and company.has_dedicated_assistant():
                    self.stdout.write(
                        self.style.WARNING(f'  → Assistant already exists, skipping (use --force to regenerate)')
                    )
                    skip_count += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(f'  → Would create assistant file for {company.name}')
                    )
                    success_count += 1
                    continue

                # Generate the assistant
                try:
                    with transaction.atomic():
                        if generate_assistant_for_existing_company(company.id):
                            self.stdout.write(
                                self.style.SUCCESS(f'  → Successfully created assistant for {company.name}')
                            )
                            success_count += 1
                        else:
                            self.stdout.write(
                                self.style.ERROR(f'  → Failed to create assistant for {company.name}')
                            )
                            error_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  → Error creating assistant for {company.name}: {e}')
                    )
                    error_count += 1

            # Summary
            self.stdout.write('\n' + '='*50)
            self.stdout.write('SUMMARY:')
            self.stdout.write(f'  Successfully processed: {success_count}')
            if skip_count > 0:
                self.stdout.write(f'  Skipped (already exist): {skip_count}')
            if error_count > 0:
                self.stdout.write(f'  Errors: {error_count}')

            if dry_run:
                self.stdout.write(
                    self.style.WARNING('\nThis was a dry run. Use without --dry-run to actually create files.')
                )
            elif success_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'\nSuccessfully generated {success_count} AI assistant(s)!')
                )

        except Exception as e:
            raise CommandError(f'Command failed: {e}')
