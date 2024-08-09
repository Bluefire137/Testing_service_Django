import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_service.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_NAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@gmail.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'password')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
