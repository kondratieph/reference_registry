import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a local superuser (idempotent)."

    def handle(self, *args, **options):
        if os.getenv('APP_ENV') != 'LOCAL_DOCKER':
        # if os.environ.get('APP_ENV') != 'LOCAL_DOCKER':
            self.stdout.write(self.style.WARNING(
                'APP_ENV is not LOCAL_DOCKER - skipping admin creation.'
            ))
            return

        User = get_user_model()
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@admin.admin')
        password = os.environ.get('ADMIN_PASSWORD', 'admin')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Superuser \'{username}\' already exists, skipping.'
            ))
            return

        User.objects.create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(self.style.SUCCESS(
            f'Superuser \'{username}\' created.')
        )
