from django.core.management.base import BaseCommand
import os
from datetime import datetime
from django.conf import settings
import glob


class Command(BaseCommand):
    help = "نسخ احتياطي تلقائي للمنيو والعملاء مع timestamp"

    def handle(self, *args, **options):
        from django.core.management import call_command

        # حفظ الـ backup في مجلد menu_backups
        backup_dir = os.path.join(settings.BASE_DIR, 'menu_backups')
        os.makedirs(backup_dir, exist_ok=True)

        # اسم الملف مع timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'menu_backup_{timestamp}.json'
        filepath = os.path.join(backup_dir, filename)

        # تصدير Category و MenuItem و Customer
        with open(filepath, 'w', encoding='utf-8') as f:
            call_command('dumpdata', 'core.Category', 'core.MenuItem', 'core.Customer',
                        indent=2, stdout=f)

        # الاحتفاظ بآخر 5 نسخ فقط
        self._cleanup_old_backups(backup_dir, keep=5)

        # حفظ اسم آخر backup في ملف reference
        latest_file = os.path.join(backup_dir, 'latest_backup.txt')
        with open(latest_file, 'w', encoding='utf-8') as f:
            f.write(filename)

        self.stdout.write(self.style.SUCCESS(f'تم حفظ النسخة الاحتياطية: {filename}'))

    def _cleanup_old_backups(self, backup_dir, keep=5):
        """حذف النسخ القديمة، الاحتفاظ بآخر n نسخ"""
        files = sorted(glob.glob(os.path.join(backup_dir, 'menu_backup_*.json')))
        for old_file in files[:-keep]:
            os.remove(old_file)
            self.stdout.write(self.style.WARNING(f'حذف النسخة القديمة: {os.path.basename(old_file)}'))
