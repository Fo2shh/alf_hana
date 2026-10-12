import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alfhana_kitchen.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create Admin user
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("✓ Admin user created: admin / admin123")
else:
    print("✓ Admin user already exists: admin / admin123")

# Create Kitchen user
if not User.objects.filter(username='kitchen').exists():
    kitchen_user = User.objects.create_user(
        username='kitchen',
        email='kitchen@example.com',
        password='kitchen123'
    )
    kitchen_user.is_staff = True
    kitchen_user.save()
    print("✓ Kitchen user created: kitchen / kitchen123")
else:
    print("✓ Kitchen user already exists: kitchen / kitchen123")

# Create Driver user
if not User.objects.filter(username='driver1').exists():
    driver_user = User.objects.create_user(
        username='driver1',
        email='driver1@example.com',
        password='driver123'
    )
    driver_user.save()
    print("✓ Driver user created: driver1 / driver123")
else:
    print("✓ Driver user already exists: driver1 / driver123")

print("\nAll default users are ready!")
