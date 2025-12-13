from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update admin superuser with username "admin" and password "admin"'

    def handle(self, *args, **kwargs):
        username = 'admin'
        email = 'admin@carhub.com'
        password = 'admin'

        try:
            # Check if admin user already exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.email = email
                user.first_name = 'Admin'
                user.last_name = 'User'
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" updated successfully!'))
            else:
                # Create new admin user
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name='Admin',
                    last_name='User'
                )
                self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully!'))
            
            self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
            self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
            self.stdout.write(self.style.WARNING('Please change the password after first login!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
