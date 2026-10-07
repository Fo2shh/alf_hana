from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from core.models import Order, MenuItem, Customer, User
from decimal import Decimal, InvalidOperation
import json


def _parse_whole_price(value):
    price = Decimal(str(value))
    if not price.is_finite() or price < 0 or price != price.to_integral_value():
        raise ValueError('يجب أن يكون السعر عددًا صحيحًا غير سالب')
    return price


def _prepare_order_items(items_data, existing_regular_prices=None, existing_discounts=None):
    if not isinstance(items_data, list) or not items_data:
        raise ValueError('يجب اختيار صنف واحد على الأقل')

    existing_regular_prices = existing_regular_prices or {}
    existing_discounts = existing_discounts or {}
    prepared_items = []
    subtotal = Decimal('0')

    for item_data in items_data:
        if not isinstance(item_data, dict):
            raise ValueError('بيانات الصنف غير صالحة')

        menu_item = get_object_or_404(MenuItem, pk=item_data.get('id'))
        quantity = int(item_data.get('quantity', 0))
        if quantity < 1:
            raise ValueError('الكمية غير صالحة')

        regular_price = existing_regular_prices.get(menu_item.pk, menu_item.price)
        discount = _parse_whole_price(
            item_data.get('discount', existing_discounts.get(menu_item.pk, 0))
        )
        if discount > regular_price:
            raise ValueError('الخصم لا يمكن أن يتجاوز سعر الوحدة')
        price = regular_price - discount

        prepared_items.append((menu_item, quantity, regular_price, price))
        subtotal += price * quantity

    return prepared_items, subtotal


@login_required
def order_list(request):
    """قائمة الطلبات"""
    from django.utils import timezone
    from datetime import timedelta
    from core.models import Order
    
    yesterday = timezone.now() - timedelta(hours=24)
    orders = Order.objects.filter(
        created_at__gte=yesterday
    ).select_related('customer', 'driver').prefetch_related('items')
    if request.user.role == 'driver':
        orders = orders.filter(driver=request.user)
    
    context = {
        'orders': orders,
    }
    if request.user.role in ('admin', 'kitchen'):
        context['drivers'] = User.objects.filter(
            role='driver', is_active=True
        ).order_by('username')
    return render(request, 'orders/order_list.html', context)


@login_required
def order_create(request):
    """إنشاء طلب جديد"""
    from core.models import Order, OrderItem

    if request.user.role not in ('admin', 'kitchen'):
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        try:
            items_data = json.loads(request.POST.get('items_data') or '[]')
            prepared_items, subtotal = _prepare_order_items(items_data)
            delivery_fee_value = request.POST.get('delivery_fee', '')
            delivery_fee = _parse_whole_price(delivery_fee_value) if delivery_fee_value else Decimal('0')
        except (InvalidOperation, TypeError, ValueError, json.JSONDecodeError):
            return HttpResponseBadRequest('تحقق من أسعار الأصناف والكميات ورسوم التوصيل')

        # بيانات العميل
        customer_id = request.POST.get('customer_id')
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_address = request.POST.get('customer_address')
        customer_google_maps_link = request.POST.get('customer_google_maps_link', '')
        customer_latitude = request.POST.get('customer_latitude', '')
        customer_longitude = request.POST.get('customer_longitude', '')

        # بيانات الطلب
        notes = request.POST.get('notes', '')

        # إنشاء الطلب
        order = Order()

        if customer_id and customer_id != 'new':
            order.customer = Customer.objects.get(id=customer_id)
        else:
            # إنشاء عميل جديد
            customer = Customer.objects.create(
                name=customer_name,
                phone=customer_phone,
                address=customer_address,
                google_maps_link=customer_google_maps_link if customer_google_maps_link else None,
                latitude=Decimal(customer_latitude) if customer_latitude else None,
                longitude=Decimal(customer_longitude) if customer_longitude else None
            )
            order.customer = customer
        
        order.delivery_fee = delivery_fee
        order.notes = notes
        order.save()
        
        # إضافة الأصناف
        for menu_item, quantity, regular_price, price in prepared_items:
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                regular_price=regular_price,
                price=price
            )
        
        order.subtotal = subtotal
        order.total = subtotal + delivery_fee
        order.save()
        
        return redirect('order_detail', pk=order.pk)
    
    context = {
        'menu_items': MenuItem.objects.filter(is_active=True).select_related('category'),
        'customers': Customer.objects.all(),
    }
    return render(request, 'orders/order_form.html', context)


@login_required
def order_detail(request, pk):
    """تفاصيل الطلب"""
    from core.models import Order
    orders = Order.objects.select_related('customer', 'driver').prefetch_related('items__menu_item')
    if request.user.role == 'driver':
        orders = orders.filter(driver=request.user)
    order = get_object_or_404(orders, pk=pk)
    items = list(order.items.all())
    context = {
        'order': order,
        'items': items,
        'has_discounts': any(item.discount_per_unit for item in items),
    }
    if request.user.role in ('admin', 'kitchen'):
        context['drivers'] = User.objects.filter(
            role='driver', is_active=True
        ).order_by('username')
    return render(request, 'orders/order_detail.html', context)


@login_required
@require_POST
def order_assign_driver(request, pk):
    """تعيين طلب لمندوب أو إلغاء تعيينه"""
    if request.user.role not in ('admin', 'kitchen'):
        return HttpResponseForbidden()

    order = get_object_or_404(Order, pk=pk)
    if order.status == 'delivered':
        return HttpResponseBadRequest('لا يمكن تغيير المندوب بعد تسليم الطلب')

    driver_id = request.POST.get('driver_id', '').strip()
    if driver_id:
        order.driver = get_object_or_404(
            User, pk=driver_id, role='driver', is_active=True
        )
        if order.status in ('new', 'preparing'):
            order.status = 'ready'
    else:
        order.driver = None

    order.save(update_fields=['driver', 'status', 'updated_at'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'driver': order.driver.username if order.driver else None,
        })
    return redirect('order_detail', pk=order.pk)


@login_required
def order_edit(request, pk):
    """تعديل الطلب"""
    from core.models import Order, OrderItem, MenuItem, Customer
    if request.user.role not in ('admin', 'kitchen'):
        return HttpResponseForbidden()
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        existing_regular_prices = dict(
            order.items.values_list('menu_item_id', 'regular_price')
        )
        existing_discounts = {
            item.menu_item_id: item.discount_per_unit
            for item in order.items.all()
        }
        try:
            items_data = json.loads(request.POST.get('items_data') or '[]')
            prepared_items, subtotal = _prepare_order_items(
                items_data, existing_regular_prices, existing_discounts
            )
            delivery_fee_value = request.POST.get('delivery_fee', '')
            delivery_fee = _parse_whole_price(delivery_fee_value) if delivery_fee_value else Decimal('0')
        except (InvalidOperation, TypeError, ValueError, json.JSONDecodeError):
            return HttpResponseBadRequest('تحقق من أسعار الأصناف والكميات ورسوم التوصيل')

        # تعديل بيانات العميل
        customer_id = request.POST.get('customer_id')
        if customer_id and customer_id != 'new':
            order.customer = Customer.objects.get(id=customer_id)
            order.customer_name = ''
            order.customer_phone = ''
            order.customer_address = ''
        else:
            order.customer = None
            order.customer_name = request.POST.get('customer_name')
            order.customer_phone = request.POST.get('customer_phone')
            order.customer_address = request.POST.get('customer_address')
        
        # تعديل رسوم التوصيل والملاحظات
        order.delivery_fee = delivery_fee
        order.notes = request.POST.get('notes', '')
        
        # حذف جميع الأصناف القديمة
        order.items.all().delete()
        
        # إضافة الأصناف الجديدة
        for menu_item, quantity, regular_price, price in prepared_items:
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                regular_price=regular_price,
                price=price
            )
        
        order.subtotal = subtotal
        order.total = subtotal + order.delivery_fee
        order.save()
        
        return redirect('order_detail', pk=order.pk)
    
    context = {
        'order': order,
        'menu_items': MenuItem.objects.filter(is_active=True).select_related('category'),
        'customers': Customer.objects.all(),
    }
    return render(request, 'orders/order_edit.html', context)


@require_POST
@login_required
def order_update_status(request, pk):
    """تحديث حالة الطلب"""
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')

    if new_status not in dict(Order.STATUS_CHOICES):
        return JsonResponse({'status': 'error'}, status=400)

    if request.user.role == 'driver':
        allowed_transitions = {
            'ready': 'delivering',
            'delivering': 'delivered',
        }
        if order.driver_id != request.user.pk:
            return JsonResponse({'status': 'error'}, status=403)
        if allowed_transitions.get(order.status) != new_status:
            return JsonResponse({'status': 'error'}, status=400)
    elif request.user.role not in ('admin', 'kitchen'):
        return JsonResponse({'status': 'error'}, status=403)

    order.status = new_status
    order.save()
    return JsonResponse({'status': 'success', 'new_status': order.status})


@login_required
def order_print(request, pk):
    """طباعة الفاتورة"""
    from core.models import Order
    orders = Order.objects.prefetch_related('items__menu_item')
    if request.user.role == 'driver':
        orders = orders.filter(driver=request.user)
    order = get_object_or_404(orders, pk=pk)
    items = list(order.items.all())
    context = {
        'order': order,
        'items': items,
        'has_discounts': any(item.discount_per_unit for item in items),
        'restaurant_name': 'الف هنا',
        'restaurant_phone': '0500000000',  # يمكن تعديله
    }
    return render(request, 'orders/order_print.html', context)
