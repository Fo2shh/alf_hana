from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import os
from datetime import datetime


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_tools(request):
    """صفحة الأدوات الإدارية"""
    backup_dir = os.path.join(settings.BASE_DIR, 'menu_backups')
    latest_file = os.path.join(backup_dir, 'latest_backup.txt')

    backups = []
    if os.path.exists(backup_dir):
        import glob
        files = sorted(glob.glob(os.path.join(backup_dir, 'menu_backup_*.json')), reverse=True)
        for f in files:
            stat = os.stat(f)
            size_kb = stat.st_size / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            backups.append({
                'filename': os.path.basename(f),
                'size': size_str,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'is_latest': os.path.exists(latest_file) and os.path.basename(f) == open(latest_file).read().strip()
            })

    return render(request, 'admin/admin_tools.html', {'backups': backups})


@login_required
@user_passes_test(is_admin)
def backup_menu_now(request):
    """نسخ احتياطي يدوي للمنيو"""
    try:
        call_command('backup_menu')
        messages.success(request, 'تم حفظ النسخة الاحتياطية بنجاح')
    except Exception as e:
        messages.error(request, f'فشل النسخ الاحتياطي: {str(e)}')
    return redirect('admin_tools')


@login_required
@user_passes_test(is_admin)
def restore_menu_now(request):
    """استعادة المنيو من آخر نسخة احتياطية"""
    if request.method == 'POST':
        try:
            call_command('restore_menu')
            messages.success(request, 'تم استعادة المنيو بنجاح')
        except Exception as e:
            messages.error(request, f'فشل الاستعادة: {str(e)}')
    return redirect('admin_tools')


@login_required
@user_passes_test(is_admin)
def delete_all_data(request):
    """حذف كل البيانات بما في ذلك المنيو والعملاء ثم استعادة المنيو والعملاء"""
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation != 'DELETE_ALL_DATA':
            messages.error(request, 'كلمة التأكيد غير صحيحة')
            return redirect('admin_tools')

        try:
            # تعطيل الـ backup مؤقتاً لتجنب إنشاء نسخة فارغة أثناء الحذف
            from core.models import set_backup_enabled
            set_backup_enabled(False)

            # حذف البيانات بالترتيب الصحيح
            from core.models import Order, OrderItem, Customer, DriverLocation, Trip, MenuItem, Category

            # حذف الطلبات وأصنافها
            OrderItem.objects.all().delete()
            Order.objects.all().delete()

            # حذف الرحلات
            Trip.objects.all().delete()

            # حذف مواقع المندوبين
            DriverLocation.objects.all().delete()

            # حذف العملاء
            Customer.objects.all().delete()

            # حذف المنيو
            MenuItem.objects.all().delete()
            Category.objects.all().delete()

            # استعادة المنيو والعملاء
            call_command('restore_menu')

            # إعادة تفعيل الـ backup
            set_backup_enabled(True)

            messages.success(request, 'تم حذف جميع البيانات واستعادة المنيو والعملاء بنجاح')
        except Exception as e:
            messages.error(request, f'فشل الحذف: {str(e)}')
    return redirect('admin_tools')


@login_required
@user_passes_test(is_admin)
def hard_reset_database(request):
    """إعادة تعيين كاملة للداتا بيز مع استعادة المنيو والعملاء"""
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation != 'HARD_RESET_DB':
            messages.error(request, 'كلمة التأكيد غير صحيحة')
            return redirect('admin_tools')

        try:
            # حذف ملف الداتا بيز
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            if os.path.exists(db_path):
                os.remove(db_path)

            # تشغيل migrations
            call_command('migrate', '--run-syncdb', verbosity=0)

            # استعادة المنيو والعملاء
            call_command('restore_menu')

            messages.success(request, 'تم إعادة تعيين الداتا بيز بنجاح (المنيو والعملاء مستعادان)')
        except Exception as e:
            messages.error(request, f'فشل إعادة التعيين: {str(e)}')
    return redirect('admin_tools')


@login_required
@user_passes_test(is_admin)
def seed_menu_now(request):
    """تشغيل seed_menu لإعادة استيراد المنيو من الملف"""
    if request.method == 'POST':
        try:
            call_command('seed_menu')
            messages.success(request, 'تم استيراد المنيو من seed_menu.py بنجاح')
        except Exception as e:
            messages.error(request, f'فشل الاستيراد: {str(e)}')
    return redirect('admin_tools')
