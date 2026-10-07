from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User, Category, MenuItem, Customer, Order, 
    OrderItem, DriverLocation, Trip
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('بيانات النظام', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('بيانات النظام', {'fields': ('email', 'role', 'phone')}),
    )
    list_display = ['username', 'email', 'role', 'phone', 'is_active']
    list_filter = DjangoUserAdmin.list_filter + ('role',)
    search_fields = ['username', 'email', 'phone']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'address', 'latitude', 'longitude', 'google_maps_link', 'total_orders', 'created_at']
    search_fields = ['name', 'phone', 'address']
    list_filter = ['created_at']
    readonly_fields = ['qr_code']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'phone', 'address')
        }),
        ('الموقع', {
            'fields': ('latitude', 'longitude', 'google_maps_link')
        }),
        ('معلومات إضافية', {
            'fields': ('notes', 'total_orders', 'qr_code')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['regular_price', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['daily_serial', 'customer_name', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'daily_serial']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'delivered_at']


@admin.register(DriverLocation)
class DriverLocationAdmin(admin.ModelAdmin):
    list_display = ['driver', 'latitude', 'longitude', 'timestamp']
    list_filter = ['driver', 'timestamp']
    readonly_fields = ['timestamp']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['driver', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'driver']
    filter_horizontal = ['orders']
