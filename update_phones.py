import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alfhana_kitchen.settings')
django.setup()

from core.models import User

# تحديث أرقام الهاتف للمستخدمين الموجودين
users = User.objects.all()
for user in users:
    if user.username == 'admin':
        user.phone = '01200000000'
    elif user.username == 'kitchen':
        user.phone = '01200000001'
    elif user.username == 'driver1':
        user.phone = '01200000002'
    user.save()
    print(f"تم تحديث رقم هاتف {user.username} إلى {user.phone}")

print("\nتم تحديث أرقام الهاتف بنجاح!")
