import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alfhana_kitchen.settings')
django.setup()

from core.models import User

# Create admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@alfhana.com',
        'role': 'admin',
        'phone': '01200000000'
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print("Admin user created successfully!")
else:
    admin_user.set_password('admin123')
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.save()
    print("Admin user already exists!")

print("Username: admin")
print("Password: admin123")

# Create kitchen user
kitchen_user, created = User.objects.get_or_create(
    username='kitchen',
    defaults={
        'email': 'kitchen@alfhana.com',
        'role': 'kitchen',
        'phone': '01200000001'
    }
)
if created:
    kitchen_user.set_password('kitchen123')
    kitchen_user.save()
    print("Kitchen user created successfully!")
else:
    kitchen_user.set_password('kitchen123')
    kitchen_user.save()
    print("Kitchen user already exists!")

print("Username: kitchen")
print("Password: kitchen123")

# Create driver user
driver_user, created = User.objects.get_or_create(
    username='driver1',
    defaults={
        'email': 'driver1@alfhana.com',
        'role': 'driver',
        'phone': '01200000002'
    }
)
if created:
    driver_user.set_password('driver123')
    driver_user.save()
    print("Driver user created successfully!")
else:
    driver_user.set_password('driver123')
    driver_user.save()
    print("Driver user already exists!")

print("Username: driver1")
print("Password: driver123")
