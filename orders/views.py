import json
import math

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from core.models import Order, MenuItem, Customer, User
from decimal import Decimal, InvalidOperation


def _safe_parse_float(value):
    """Safely parse a coordinate string into a float, returning None on any error.

    Never raises ValueError — matches project rule: coordinate inputs must be
    processed with exception-free helpers to avoid crashes from bad text/links.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        f = float(s)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(f):
        return None
    return f


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

        # Check if this is a custom item (id is null or missing)
        is_custom = item_data.get('isCustom', False) or item_data.get('id') is None

        if is_custom:
            # Handle custom item
            name = item_data.get('name', '').strip()
            price = Decimal(str(item_data.get('price', 0)))
            description = item_data.get('description', '').strip()
            quantity = int(item_data.get('quantity', 0))

            if not name:
                raise ValueError('اسم الصنف المخصص مطلوب')
            if quantity < 1:
                raise ValueError('الكمية غير صالحة')
            if price < 0:
                raise ValueError('السعر غير صالح')

            # Custom item: (None, name, price, description, quantity, is_custom=True)
            prepared_items.append((None, name, price, description, quantity, True))
            subtotal += price * quantity
        else:
            # Handle regular menu item
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

            # Regular item: (menu_item, quantity, regular_price, price, is_custom=False)
            prepared_items.append((menu_item, quantity, regular_price, price, False))
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


def _build_menu_context():
    """Build menu picker context: categories, grouped items, top-sellers.

    NOTE: Returns raw Python objects (dicts/lists) for Django's |json_script
    filter to serialize SAFELY. Do NOT pre-json.dumps() them, because the
    |json_script template filter serializes Python objects itself — doing
    both produces double-escaped strings that JSON.parse() can't turn into
    arrays (the root cause of the "0 items visible" blank grid bug).
    """
    from django.db import models
    from django.db.models import Count, Sum
    from core.models import Category

    active_items_qs = (
        MenuItem.objects
        .filter(is_active=True)
        .select_related('category')
        .order_by('category__order', 'order', 'name')
    )
    active_items = list(active_items_qs)

    # ---- 1) Categories with active-item counts ----
    categories = list(
        Category.objects
        .filter(items__is_active=True)
        .annotate(item_count=Count('items', filter=models.Q(items__is_active=True)))
        .order_by('order')
        .distinct()
    )

    # ---- 2) Top 8 sellers: by aggregate OrderItem quantity (fallback: first 8) ----
    top_sellers = list(
        MenuItem.objects
        .filter(is_active=True)
        .annotate(_sold=Sum('orderitem__quantity'))
        .order_by('-_sold', 'order', 'name')[:8]
    )
    if len(top_sellers) < 8:
        seen_ids = {t.id for t in top_sellers}
        fallback = [it for it in active_items if it.id not in seen_ids]
        top_sellers.extend(fallback[: 8 - len(top_sellers)])

    # ---- 3) Group items by category (stable order) ----
    grouped = {cat.id: [] for cat in categories}
    for item in active_items:
        grouped.setdefault(item.category_id, []).append(item)

    # ---- 4) Raw Python objects for |json_script (will be serialized by Django) ----
    def _serialize(it):
        return {
            "id": it.id,
            "n": it.name,
            "p": int(it.price),
            "c": it.category_id,
            "cn": it.category.name,
            "w": int(it.price) == 0,
        }

    items_payload = [_serialize(it) for it in active_items]
    top_ids_payload = [int(t.id) for t in top_sellers]

    return {
        "menu_items": active_items,           # backwards-compat
        "menu_items_payload": items_payload,   # to be piped through |json_script
        "menu_categories": categories,
        "menu_grouped": grouped,
        "menu_top_sellers": top_sellers,
        "menu_top_ids_payload": top_ids_payload,  # to be piped through |json_script
    }


def _resolve_customer_from_post(request):
    """Resolve a customer safely from POST payload with strict server-side validation.

    Returns a 4-tuple:
        (customer_obj, error_message, was_created, anon_fields_dict)

    On success:
        customer_obj       -> a Customer instance (either existing or just created)
        error_message      -> None
        was_created        -> bool (True if newly inserted, False if existing)
        anon_fields_dict   -> {} (anonymous data left blank on anon mode unused)

    On failure:
        customer_obj       -> None
        error_message      -> Arabic user-facing error string
        was_created        -> False
        anon_fields_dict   -> {}

    Never raises DB exceptions (IntegrityError / DoesNotExist).
    """
    from core.models import Customer

    cid = (request.POST.get('customer_id') or '').strip()
    name = (request.POST.get('customer_name') or '').strip()
    phone = (request.POST.get('customer_phone') or '').strip()
    address = (request.POST.get('customer_address') or '').strip()
    gmaps = (request.POST.get('customer_google_maps_link') or '').strip()
    lat_raw = (request.POST.get('customer_latitude') or '').strip()
    lng_raw = (request.POST.get('customer_longitude') or '').strip()

    # --- Case A: Existing customer chosen from dropdown
    if cid and cid != 'new':
        if not cid.isdigit():
            return None, 'معرف العميل غير صالح (يجب أن يكون رقمًا)', False, {}
        existing = Customer.objects.filter(pk=int(cid)).first()
        if not existing:
            return None, 'العميل المحدد غير موجود في قاعدة البيانات', False, {}
        return existing, None, False, {}

    # --- Case B: New customer (or no choice)
    if not name:
        return None, 'اسم العميل مطلوب — يرجى إدخال اسم العميل لإنشاء عميل جديد', False, {}
    if not phone:
        return None, 'رقم الهاتف مطلوب — يرجى إدخال رقم هاتف العميل', False, {}

    lat = _safe_parse_float(lat_raw)
    lng = _safe_parse_float(lng_raw)

    try:
        created = Customer.objects.create(
            name=name,
            phone=phone,
            address=address or '',
            google_maps_link=gmaps or None,
            latitude=lat,
            longitude=lng,
        )
    except Exception as exc:  # noqa: BLE001
        return None, f'فشل إنشاء العميل: {str(exc)}', False, {}
    return created, None, True, {}


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

        # ---- Resolve customer (safe: never raises DB errors) ----
        customer, cust_error, _was_new, _anon = _resolve_customer_from_post(request)
        if customer is None:
            ctx = _build_menu_context()
            ctx['customers'] = Customer.objects.all()
            ctx['validation_error'] = cust_error or 'تعذر التعرف على بيانات العميل'
            return render(request, 'orders/order_form.html', ctx, status=400)

        # بيانات الطلب
        notes = request.POST.get('notes', '')

        # إنشاء الطلب
        order = Order()
        order.customer = customer
        order.delivery_fee = delivery_fee
        order.notes = notes
        order.save()
        
        # إضافة الأصناف
        for item_data in prepared_items:
            if len(item_data) == 6 and item_data[5]:  # is_custom=True
                # Custom item: (None, name, price, description, quantity, True)
                _, name, price, description, quantity, _ = item_data
                OrderItem.objects.create(
                    order=order,
                    menu_item=None,
                    custom_item_name=name,
                    custom_item_price=price,
                    custom_item_description=description,
                    quantity=quantity,
                    regular_price=price,
                    price=price
                )
            else:
                # Regular item: (menu_item, quantity, regular_price, price, False)
                menu_item, quantity, regular_price, price, _ = item_data
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
    
    ctx = _build_menu_context()
    ctx['customers'] = Customer.objects.all()
    return render(request, 'orders/order_form.html', ctx)


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
            order.items.filter(menu_item__isnull=False).values_list('menu_item_id', 'regular_price')
        )
        existing_discounts = {
            item.menu_item_id: item.discount_per_unit
            for item in order.items.filter(menu_item__isnull=False)
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

        # ---- تعديل بيانات العميل (صارم — لا أخطاء قاعدة بيانات) ----
        customer, cust_error, _was_new, _anon = _resolve_customer_from_post(request)
        if customer is None:
            ctx = _build_menu_context()
            ctx['order'] = order
            ctx['customers'] = Customer.objects.all()
            ctx['validation_error'] = cust_error or 'تعذر التعرف على بيانات العميل'
            return render(request, 'orders/order_edit.html', ctx, status=400)

        order.customer = customer
        # In this project the Order model stores BOTH an FK customer AND
        # denormalized name/phone/address fields. When we have an FK, clear
        # the denormalized copies so they never disagree with the FK.
        order.customer_name = ''
        order.customer_phone = ''
        order.customer_address = ''

        # تعديل رسوم التوصيل والملاحظات
        order.delivery_fee = delivery_fee
        order.notes = request.POST.get('notes', '')

        # حذف جميع الأصناف القديمة
        order.items.all().delete()

        # إضافة الأصناف الجديدة
        for item_data in prepared_items:
            if len(item_data) == 6 and item_data[5]:  # is_custom=True
                # Custom item: (None, name, price, description, quantity, True)
                _, name, price, description, quantity, _ = item_data
                OrderItem.objects.create(
                    order=order,
                    menu_item=None,
                    custom_item_name=name,
                    custom_item_price=price,
                    custom_item_description=description,
                    quantity=quantity,
                    regular_price=price,
                    price=price
                )
            else:
                # Regular item: (menu_item, quantity, regular_price, price, False)
                menu_item, quantity, regular_price, price, _ = item_data
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

    ctx = _build_menu_context()
    ctx['order'] = order
    ctx['customers'] = Customer.objects.all()
    return render(request, 'orders/order_edit.html', ctx)


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
    
    # Format time in 12-hour format with AM/PM in English
    import datetime
    order_time = order.created_at.strftime('%I:%M %p')
    
    context = {
        'order': order,
        'items': items,
        'has_discounts': any(item.discount_per_unit for item in items),
        'restaurant_name': 'الف هنا',
        'restaurant_phone': '01206622290',
        'order_time': order_time,
    }
    return render(request, 'orders/order_print.html', context)
