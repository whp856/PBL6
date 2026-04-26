import os
import django

# 设置 Django 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbl6.settings')
django.setup()

from user.models import User

# 检查是否已存在超级用户
if not User.objects.filter(is_superuser=True).exists():
    # 创建超级用户
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print('超级用户创建成功！')
else:
    print('超级用户已存在，跳过创建。')
