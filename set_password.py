#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbl6.settings')

import django
django.setup()

from user.models import User

try:
    user = User.objects.get(email='admin@example.com')
    user.set_password('admin123')
    user.save()
    print('Password set successfully')
except User.DoesNotExist:
    print('User not found')
