from django.core.management.base import BaseCommand
import os
from django.conf import settings
from django.db.models.signals import post_save, post_delete


class Command(BaseCommand):
    help = "استعادة المنيو والعملاء من آخر نسخة احتياطية"

    def handle(self, *args, **options):
        # تعطيل الـ backup مؤقتاً لتجنب حلقة لا نهائية
        from core.models import set_backup_enabled
        set_backup_enabled(False)

        backup_dir = os.path.join(settings.BASE_DIR, 'menu_backups')
        latest_file = os.path.join(backup_dir, 'latest_backup.txt')

        if not os.path.exists(latest_file):
            self.stdout.write(self.style.WARNING('لا توجد نسخة احتياطية'))
            set_backup_enabled(True)
            return

        with open(latest_file, 'r', encoding='utf-8') as f:
            filename = f.read().strip()

        filepath = os.path.join(backup_dir, filename)

        if not os.path.exists(filepath):
            self.stdout.write(self.style.ERROR(f'الملف {filename} غير موجود'))
            set_backup_enabled(True)
            return

        from django.core.management import call_command
        call_command('loaddata', filepath)

        self.stdout.write(self.style.SUCCESS(f'تم استعادة المنيو والعملاء من: {filename}'))

        # إعادة تفعيل الـ backup
        set_backup_enabled(True)
