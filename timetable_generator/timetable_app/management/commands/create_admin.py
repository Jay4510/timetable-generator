from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a superuser admin account'

    def handle(self, *args, **options):
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(
                self.style.SUCCESS('Successfully created admin user')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )