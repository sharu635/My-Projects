import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# create a test user
user, created = User.objects.get_or_create(username='testuser')
if created:
    user.set_password('testpass')
    user.save()

client = Client()
client.force_login(user)
response = client.get('/')
with open('rendered_home.html', 'w') as f:
    f.write(response.content.decode('utf-8'))
print("Rendered home.html written.")
