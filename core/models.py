from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image


class User(AbstractUser):
    """نظام المستخدمين المخصص مع أدوار متعددة"""
    ROLE_CHOICES = [
        ('admin', 'أدمن'),
        ('kitchen', 'مطبخ'),
        ('driver', 'مندوب'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='kitchen')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Category(models.Model):
    """أقسام المنيو"""
    name = models.CharField(max_length=100, verbose_name='اسم القسم')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'قسم'
        verbose_name_plural = 'أقسام المنيو'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """أصناف المنيو"""
    name = models.CharField(max_length=200, verbose_name='اسم الصنف')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', verbose_name='القسم')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='السعر')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True, verbose_name='صورة')
    order = models.IntegerField(default=0, verbose_name='الترتيب')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'صنف'
        verbose_name_plural = 'أصناف المنيو'
        ordering = ['category__order', 'order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.price} ريال"


class Customer(models.Model):
    """العملاء"""
    name = models.CharField(max_length=200, verbose_name='اسم العميل')
    phone = models.CharField(max_length=11, unique=True, verbose_name='رقم الهاتف')
    address = models.TextField(verbose_name='العنوان')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name='خط العرض')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name='خط الطول')
    google_maps_link = models.URLField(blank=True, null=True, verbose_name='رابط خرائط جوجل')
    qr_code = models.ImageField(upload_to='customer_qr/', blank=True, null=True, verbose_name='رمز QR')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.phone}"

    @property
    def total_orders(self):
        """إجمالي الطلبات للعميل"""
        return self.orders.count()
    
    def save(self, *args, **kwargs):
        # استخدام الرابط المدخل من المستخدم، أو توليد رابط من الإحداثيات
        if self.google_maps_link:
            # إذا كان الرابط مدخل يدوياً، نستخدمه كما هو
            pass
        elif self.latitude and self.longitude:
            # إذا لم يكن هناك رابط مدخل وتوجد إحداثيات، نولد رابط
            self.google_maps_link = f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        else:
            # إذا لم يكن هناك رابط ولا إحداثيات، نحذف الرابط القديم
            self.google_maps_link = None

        # إنشاء أو تحديث QR Code إذا كان الرابط موجوداً
        if self.google_maps_link:
            # حذف الملف القديم إذا كان موجوداً
            if self.qr_code:
                try:
                    self.qr_code.delete(save=False)
                except:
                    pass

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.google_maps_link)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # حفظ الصورة باسم فريد يتضمن الطابع الزمني
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            import time
            timestamp = int(time.time())
            file_name = f'qr_{self.phone}_{timestamp}.png'
            self.qr_code.save(file_name, File(buffer), save=False)
        else:
            # إذا لم يكن هناك رابط، حذف QR Code القديم
            if self.qr_code:
                try:
                    self.qr_code.delete(save=False)
                except:
                    pass

        super().save(*args, **kwargs)


class Order(models.Model):
    """الطلبات"""
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('preparing', 'قيد التحضير'),
        ('ready', 'جاهز'),
        ('delivering', 'قيد التوصيل'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي'),
    ]
    
    daily_serial = models.IntegerField(verbose_name='الرقم التسلسلي اليومي')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='العميل')
    customer_name = models.CharField(max_length=200, blank=True, verbose_name='اسم العميل (يدوي)')
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف (يدوي)')
    customer_address = models.TextField(blank=True, verbose_name='العنوان (يدوي)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='الحالة')
    subtotal = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='المجموع الفرعي')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='رسوم التوصيل')
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='الإجمالي')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', verbose_name='المندوب')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='وقت التسليم')
    
    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']
    
    def __str__(self):
        customer_display = self.customer.name if self.customer else self.customer_name
        return f"طلب #{self.daily_serial} - {customer_display}"

    @property
    def discount_total(self):
        return sum(item.discount_per_unit * item.quantity for item in self.items.all())

    def save(self, *args, **kwargs):
        if not self.daily_serial:
            # الحصول على آخر رقم تسلسلي اليوم
            today = timezone.now().date()
            last_order = Order.objects.filter(created_at__date=today).order_by('-daily_serial').first()
            self.daily_serial = (last_order.daily_serial + 1) if last_order else 1
        
        if self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """أصناف الطلب"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='الطلب')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, null=True, blank=True, verbose_name='الصنف')
    custom_item_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='اسم الصنف المخصص')
    custom_item_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name='سعر الصنف المخصص')
    custom_item_description = models.TextField(blank=True, null=True, verbose_name='وصف الصنف المخصص')
    quantity = models.IntegerField(default=1, verbose_name='الكمية')
    regular_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name='سعر القائمة')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='السعر')
    subtotal = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='المجموع')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')

    class Meta:
        verbose_name = 'صنف في الطلب'
        verbose_name_plural = 'أصناف الطلب'

    def save(self, *args, **kwargs):
        if self.menu_item and self.regular_price is None:
            self.regular_price = self.menu_item.price
        elif self.custom_item_price and self.regular_price is None:
            self.regular_price = self.custom_item_price
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

    @property
    def discount_per_unit(self):
        if self.regular_price:
            return max(self.regular_price - self.price, 0)
        return 0

    @property
    def item_name(self):
        """إرجاع اسم الصنف (من المنيو أو مخصص)"""
        if self.menu_item:
            return self.menu_item.name
        return self.custom_item_name or 'صنف غير محدد'

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"


class DriverLocation(models.Model):
    """تتبع موقع المندوب"""
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations', verbose_name='المندوب')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='خط العرض')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='خط الطول')
    accuracy = models.FloatField(blank=True, null=True, verbose_name='الدقة (متر)')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='التوقيت')
    
    class Meta:
        verbose_name = 'موقع مندوب'
        verbose_name_plural = 'مواقع المناديب'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['driver', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.driver.username} - {self.timestamp}"


class DriverCurrentLocation(models.Model):
    """أحدث موقع معروف للمندوب لاستخدامه كعلامة مباشرة على الخريطة"""
    driver = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='current_location',
        verbose_name='المندوب',
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='خط العرض')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='خط الطول')
    accuracy = models.FloatField(blank=True, null=True, verbose_name='الدقة (متر)')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        verbose_name = 'الموقع الحالي للمندوب'
        verbose_name_plural = 'المواقع الحالية للمناديب'

    def __str__(self):
        return f"{self.driver.username} - {self.updated_at}"


class Trip(models.Model):
    """رحلة المندوب"""
    STATUS_CHOICES = [
        ('started', 'بدأت'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'انتهت'),
    ]
    
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips', verbose_name='المندوب')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started', verbose_name='الحالة')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت البدء')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='وقت الانتهاء')
    orders = models.ManyToManyField(Order, related_name='trips', verbose_name='الطلبات')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    
    class Meta:
        verbose_name = 'رحلة'
        verbose_name_plural = 'رحلات المناديب'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"رحلة {self.driver.username} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


# ============================================================
# AUTO-BACKUP SIGNALS
# ============================================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.management import call_command
from threading import Thread
import os

# Flag to prevent backup during restore operations
_BACKUP_ENABLED = True


def is_backup_enabled():
    """Check if backup is enabled (not during restore operations)"""
    global _BACKUP_ENABLED
    return _BACKUP_ENABLED


def set_backup_enabled(enabled):
    """Enable or disable backup"""
    global _BACKUP_ENABLED
    _BACKUP_ENABLED = enabled


def backup_menu_async():
    """تشغيل backup في thread منفصل لتجنب التأخير"""
    if not is_backup_enabled():
        return
    try:
        call_command('backup_menu')
    except Exception as e:
        print(f"Backup failed: {e}")


@receiver(post_save, sender=MenuItem)
@receiver(post_save, sender=Category)
@receiver(post_save, sender=Customer)
@receiver(post_delete, sender=MenuItem)
@receiver(post_delete, sender=Category)
@receiver(post_delete, sender=Customer)
def auto_backup_on_change(sender, instance, **kwargs):
    """نسخ احتياطي تلقائي بعد أي تعديل على المنيو والعملاء"""
    # تشغيل في thread منفصل لتجنب إبطاء الـ save
    # استخدام daemon=False لضمان اكتمال الـ backup
    t = Thread(target=backup_menu_async, daemon=False)
    t.start()
