"""
Management command to set up AI assistant permissions and assign them to users.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from saia.permissions import (
    ensure_ai_permissions_exist,
    assign_customer_permissions,
    assign_admin_permissions
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up AI assistant permissions and assign them to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--assign-all',
            action='store_true',
            help='Assign permissions to all existing users based on their roles',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Assign permissions to a specific user by username',
        )

    def handle(self, *args, **options):
        self.stdout.write('Setting up AI assistant permissions...')
        
        # Create permissions
        created_permissions = ensure_ai_permissions_exist()
        if created_permissions:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(created_permissions)} new permissions'
                )
            )
        else:
            self.stdout.write('All permissions already exist')

        # Assign permissions to users
        if options['assign_all']:
            self.assign_all_users()
        elif options['user']:
            self.assign_user(options['user'])
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Use --assign-all to assign permissions to all users, '
                    'or --user <username> to assign to a specific user'
                )
            )

    def assign_all_users(self):
        """Assign permissions to all users based on their roles"""
        users = User.objects.all()
        customer_count = 0
        admin_count = 0
        
        for user in users:
            if hasattr(user, 'is_customer') and user.is_customer:
                assign_customer_permissions(user)
                customer_count += 1
                self.stdout.write(f'Assigned customer permissions to {user.username}')
            elif user.is_staff:
                assign_admin_permissions(user)
                admin_count += 1
                self.stdout.write(f'Assigned admin permissions to {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Assigned permissions to {customer_count} customers and {admin_count} admins'
            )
        )

    def assign_user(self, username):
        """Assign permissions to a specific user"""
        try:
            user = User.objects.get(username=username)
            
            if hasattr(user, 'is_customer') and user.is_customer:
                assign_customer_permissions(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned customer permissions to {username}'
                    )
                )
            elif user.is_staff:
                assign_admin_permissions(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned admin permissions to {username}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'User {username} is neither customer nor admin - no permissions assigned'
                    )
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} does not exist')
            )
