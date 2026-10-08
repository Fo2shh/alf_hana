from django.db import migrations


def restore_menu_on_migrate(apps, schema_editor):
    """استعادة المنيو تلقائياً بعد migration - فقط إذا وجد backup"""
    from django.core.management import call_command
    try:
        call_command('restore_menu')
    except Exception as e:
        print(f"Restore failed or no backup found: {e}")


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_alter_menuitem_options_menuitem_order'),
    ]

    operations = [
        migrations.RunPython(restore_menu_on_migrate, migrations.RunPython.noop),
    ]
