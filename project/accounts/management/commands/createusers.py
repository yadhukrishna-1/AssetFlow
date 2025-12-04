from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from accounts.models import User

class Command(BaseCommand):
    help = 'Create users with specified roles (similar to Django admin createsuperuser)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the user')
        parser.add_argument('--email', type=str, help='Email for the user')
        parser.add_argument('--first-name', type=str, help='First name for the user')
        parser.add_argument('--last-name', type=str, help='Last name for the user')
        parser.add_argument('--role', type=str, choices=['admin', 'asset_manager', 'employee'], 
                          help='Role for the user')
        parser.add_argument('--password', type=str, help='Password for the user')
        parser.add_argument('--batch', action='store_true', 
                          help='Create multiple sample users at once')

    def handle(self, *args, **options):
        if options['batch']:
            self.create_sample_users()
        else:
            self.create_single_user(options)

    def create_single_user(self, options):
        username = options.get('username')
        email = options.get('email')
        first_name = options.get('first_name')
        last_name = options.get('last_name')
        role = options.get('role')
        password = options.get('password')

        # Interactive input if not provided
        if not username:
            username = input('Username: ')
        if not email:
            email = input('Email: ')
        if not first_name:
            first_name = input('First name: ')
        if not last_name:
            last_name = input('Last name: ')
        if not role:
            self.stdout.write('Available roles: admin, asset_manager, employee')
            role = input('Role: ')
        if not password:
            import getpass
            password = getpass.getpass('Password: ')

        # Validate role
        if role not in ['admin', 'asset_manager', 'employee']:
            raise CommandError('Invalid role. Choose from: admin, asset_manager, employee')

        # Check admin restriction
        if role == 'admin' and User.objects.filter(role='admin').exists():
            raise CommandError('Only one admin user is allowed in the system.')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username "{username}" already exists.')

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {role} user: {username}')
            )
        except Exception as e:
            raise CommandError(f'Error creating user: {str(e)}')

    def create_sample_users(self):
        """Create a set of sample users for testing"""
        sample_users = [
            {
                'username': 'admin',
                'email': 'admin@company.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'password': 'admin123'
            },
            {
                'username': 'manager1',
                'email': 'manager1@company.com',
                'first_name': 'Asset',
                'last_name': 'Manager',
                'role': 'asset_manager',
                'password': 'manager123'
            },
            {
                'username': 'manager2',
                'email': 'manager2@company.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'asset_manager',
                'password': 'manager123'
            },
            {
                'username': 'emp1',
                'email': 'emp1@company.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'employee',
                'password': 'employee123'
            },
            {
                'username': 'emp2',
                'email': 'emp2@company.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'employee',
                'password': 'employee123'
            },
            {
                'username': 'emp3',
                'email': 'emp3@company.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'role': 'employee',
                'password': 'employee123'
            }
        ]

        created_count = 0
        for user_data in sample_users:
            # Skip if user already exists
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {user_data["username"]} already exists, skipping...')
                )
                continue

            # Skip admin if one already exists
            if user_data['role'] == 'admin' and User.objects.filter(role='admin').exists():
                self.stdout.write(
                    self.style.WARNING('Admin user already exists, skipping admin creation...')
                )
                continue

            try:
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password=user_data['password'],
                    role=user_data['role']
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created {user_data["role"]}: {user_data["username"]}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating {user_data["username"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nBatch creation completed. Created {created_count} users.')
        )
        if created_count > 0:
            self.stdout.write('\nDefault passwords:')
            self.stdout.write('- Admin: admin123')
            self.stdout.write('- Asset Managers: manager123')
            self.stdout.write('- Employees: employee123')