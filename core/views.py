from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Prefetch
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
import math
from .models import Category, MenuItem, Customer, User, DriverLocation, DriverCurrentLocation
from django.views.decorators.http import require_POST
import json


def is_admin(user):
    return user.role == 'admin'


def is_admin_or_kitchen(user):
    return user.role in ['admin', 'kitchen']


@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية"""
    from .models import Order

    order_range = 'all' if request.GET.get('range') == 'all' else 'today'
    orders = Order.objects.all()
    if order_range == 'today':
        from datetime import timedelta
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        orders = orders.filter(created_at__gte=today_start, created_at__lt=today_end)
    orders = orders.select_related('customer', 'driver').prefetch_related('items__menu_item')
    if request.user.role == 'driver':
        orders = orders.filter(driver=request.user)

    page_obj = Paginator(orders, 30).get_page(request.GET.get('page'))
    
    context = {
        'recent_orders': page_obj.object_list,
        'page_obj': page_obj,
        'order_range': order_range,
        'user': request.user,
    }
    if request.user.role in ('admin', 'kitchen'):
        context['drivers'] = User.objects.filter(
            role='driver', is_active=True
        ).order_by('username')
    return render(request, 'core/dashboard.html', context)


@login_required
def menu_management(request):
    """عرض المنيو أو إدارته حسب دور المستخدم"""
    if request.user.role not in ('admin', 'kitchen', 'driver'):
        return HttpResponseForbidden()

    can_manage_menu = request.user.role in ('admin', 'kitchen')
    categories = Category.objects.all()
    if can_manage_menu:
        categories = categories.prefetch_related('items')
    else:
        categories = Category.objects.filter(is_active=True).prefetch_related(
            Prefetch('items', queryset=MenuItem.objects.filter(is_active=True))
        )

    context = {
        'categories': categories,
        'can_manage_menu': can_manage_menu,
    }
    return render(request, 'core/menu_management.html', context)


@login_required
@user_passes_test(is_admin)
def customers_list(request):
    """قائمة العملاء"""
    customers = Customer.objects.all().order_by('-created_at')
    context = {
        'customers': customers,
    }
    return render(request, 'core/customers_list.html', context)


@login_required
@user_passes_test(is_admin)
def customer_add(request):
    """إضافة عميل جديد"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        google_maps_link = request.POST.get('google_maps_link', '')

        # تحويل الفاصلة إلى نقطة للإحداثيات
        if latitude:
            lat_float = float(latitude.replace(',', '.'))
        else:
            lat_float = None

        if longitude:
            lng_float = float(longitude.replace(',', '.'))
        else:
            lng_float = None

        customer = Customer.objects.create(
            name=name,
            phone=phone,
            address=address,
            latitude=lat_float,
            longitude=lng_float,
            google_maps_link=google_maps_link if google_maps_link else None
        )
        return redirect('customers_list')
    
    return render(request, 'core/customer_form.html')


@login_required
@user_passes_test(is_admin)
def customer_edit(request, pk):
    """تعديل عميل"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')
        customer.google_maps_link = request.POST.get('google_maps_link', '') or None

        # تحويل الفاصلة إلى نقطة للإحداثيات
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if latitude:
            customer.latitude = float(latitude.replace(',', '.'))
        else:
            customer.latitude = None

        if longitude:
            customer.longitude = float(longitude.replace(',', '.'))
        else:
            customer.longitude = None

        customer.save()
        return redirect('customers_list')
    
    context = {'customer': customer}
    return render(request, 'core/customer_form.html', context)


@login_required
@user_passes_test(is_admin)
def customer_delete(request, pk):
    """حذف عميل"""
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customers_list')


@login_required
@user_passes_test(is_admin_or_kitchen)
def category_list(request):
    """قائمة الأقسام"""
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'core/category_list.html', context)


@login_required
@user_passes_test(is_admin_or_kitchen)
def category_add(request):
    """إضافة قسم جديد"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'

        Category.objects.create(
            name=name,
            description=description,
            order=int(order),
            is_active=is_active
        )
        return redirect('menu_management')

    return render(request, 'core/category_form.html')


@login_required
@user_passes_test(is_admin_or_kitchen)
def category_edit(request, pk):
    """تعديل قسم"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.order = int(request.POST.get('order', 0))
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        return redirect('menu_management')

    context = {'category': category}
    return render(request, 'core/category_form.html', context)


@login_required
@user_passes_test(is_admin_or_kitchen)
def category_delete(request, pk):
    """حذف قسم"""
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('menu_management')


@login_required
@user_passes_test(is_admin_or_kitchen)
def menu_item_add(request):
    """إضافة صنف جديد"""
    categories = Category.objects.all().order_by('order', 'name')

    if request.method == 'POST':
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')

        MenuItem.objects.create(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            is_active=is_active,
            image=image
        )
        return redirect('menu_management')

    context = {'categories': categories}
    return render(request, 'core/menu_item_form.html', context)


@login_required
@user_passes_test(is_admin_or_kitchen)
def menu_item_edit(request, pk):
    """تعديل صنف"""
    item = get_object_or_404(MenuItem, pk=pk)
    categories = Category.objects.all().order_by('order', 'name')

    if request.method == 'POST':
        item.category_id = request.POST.get('category')
        item.name = request.POST.get('name')
        item.description = request.POST.get('description', '')
        item.price = request.POST.get('price')
        item.is_active = request.POST.get('is_active') == 'on'
        if request.FILES.get('image'):
            item.image = request.FILES.get('image')
        item.save()
        return redirect('menu_management')

    context = {'item': item, 'categories': categories}
    return render(request, 'core/menu_item_form.html', context)


@login_required
@user_passes_test(is_admin_or_kitchen)
def menu_item_delete(request, pk):
    """حذف صنف"""
    item = get_object_or_404(MenuItem, pk=pk)
    item.delete()
    return redirect('menu_management')


@login_required
@user_passes_test(is_admin)
def drivers_list(request):
    """قائمة المناديب"""
    drivers = User.objects.filter(role='driver')
    context = {
        'drivers': drivers,
    }
    return render(request, 'core/drivers_list.html', context)


@login_required
@user_passes_test(is_admin)
def drivers_map(request):
    """خريطة المناديب الحية"""
    from django.conf import settings

    drivers = User.objects.filter(role='driver')
    context = {
        'drivers': drivers,
        'mapbox_access_token': getattr(settings, 'MAPBOX_ACCESS_TOKEN', ''),
    }
    return render(request, 'core/drivers_map.html', context)


@login_required
@user_passes_test(lambda u: u.role == 'driver')
def driver_app(request):
    """تطبيق المندوب للموبايل"""
    from django.conf import settings
    from django.core.serializers.json import DjangoJSONEncoder
    import json
    import re
    from urllib.parse import urlparse, parse_qs

    def extract_coordinates_from_link(link):
        """استخراج الإحداثيات من لينك Google Maps - دالة محسنة"""
        if not link:
            return None, None

        try:
            # أنماط مختلفة لروابط Google Maps
            patterns = [
                # @lat,lng,zoom
                r'@(-?\d+\.\d+),(-?\d+\.\d+)',
                # destination=lat,lng
                r'destination=([+-]?\d+\.\d+),([+-]?\d+\.\d+)',
                # q=lat,lng (coordinates query)
                r'q=([+-]?\d+\.\d+),([+-]?\d+\.\d+)',
                # ll=lat,lng
                r'll=([+-]?\d+\.\d+),([+-]?\d+\.\d+)',
                # lat,lng in URL path
                r'/([+-]?\d+\.\d+),([+-]?\d+\.\d+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, link)
                if match:
                    try:
                        lat = float(match.group(1))
                        lng = float(match.group(2))
                        # التحقق من صحة الإحداثيات
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            return lat, lng
                    except (ValueError, IndexError):
                        continue

            # محاولة تحليل URL parameters
            parsed = urlparse(link)
            if parsed.query:
                params = parse_qs(parsed.query)
                # البحث عن lat/lng في parameters
                for key in ['lat', 'latitude', 'center']:
                    if key in params and 'lng' in params:
                        try:
                            lat = float(params[key][0])
                            lng = float(params['lng'][0])
                            if -90 <= lat <= 90 and -180 <= lng <= 180:
                                return lat, lng
                        except (ValueError, IndexError):
                            continue

                # البحث عن center parameter (lat,lng format)
                if 'center' in params:
                    center = params['center'][0]
                    if ',' in center:
                        try:
                            parts = center.split(',')
                            lat = float(parts[0])
                            lng = float(parts[1])
                            if -90 <= lat <= 90 and -180 <= lng <= 180:
                                return lat, lng
                        except (ValueError, IndexError):
                            pass

        except Exception as e:
            print(f"Error extracting coordinates from link: {e}")

        return None, None

    orders = request.user.assigned_orders.exclude(
        status__in=['delivered', 'cancelled']
    ).select_related('customer').prefetch_related('items__menu_item')

    # تحويل الطلبات إلى JSON للإستخدام في JavaScript
    orders_data = []
    for order in orders:
        order_data = {
            'pk': order.pk,
            'daily_serial': order.daily_serial,
            'status': order.status,
        }

        if order.customer:
            # محاولة استخراج الإحداثيات من لينك Google Maps أولاً
            lat = None
            lng = None

            # الأولوية للينك Google Maps
            if order.customer.google_maps_link:
                lat, lng = extract_coordinates_from_link(order.customer.google_maps_link)

            # إذا لم تنجح، استخدم الإحداثيات من قاعدة البيانات
            if (not lat or not lng):
                lat = order.customer.latitude
                lng = order.customer.longitude

            order_data['customer'] = {
                'name': order.customer.name,
                'latitude': float(lat) if lat else None,
                'longitude': float(lng) if lng else None,
                'address': order.customer.address,
                'google_maps_link': order.customer.google_maps_link,
            }
        else:
            # للعملاء غير المسجلين (البيانات المدخلة يدوياً)
            order_data['customer'] = {
                'name': order.customer_name,
                'latitude': None,
                'longitude': None,
                'address': order.customer_address,
                'google_maps_link': None,
            }

        orders_data.append(order_data)

    orders_json = json.dumps(orders_data, cls=DjangoJSONEncoder)

    context = {
        'driver': request.user,
        'orders': orders,
        'orders_json': orders_json,
        'mapbox_access_token': getattr(settings, 'MAPBOX_ACCESS_TOKEN', ''),
    }
    return render(request, 'core/driver_app.html', context)


@login_required
def api_customer_search(request):
    """API للبحث عن العملاء"""
    query = request.GET.get('q', '')
    customers = Customer.objects.filter(
        name__icontains=query
    ) | Customer.objects.filter(
        phone__icontains=query
    )
    
    results = []
    for customer in customers[:10]:
        results.append({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'address': customer.address,
        })
    
    return JsonResponse({'results': results})


@login_required
def api_menu_search(request):
    """API للبحث عن أصناف المنيو"""
    query = request.GET.get('q', '')
    items = MenuItem.objects.filter(
        name__icontains=query,
        is_active=True
    ).select_related('category')
    
    results = []
    for item in items[:20]:
        results.append({
            'id': item.id,
            'name': item.name,
            'price': str(item.price),
            'category': item.category.name,
        })
    
    return JsonResponse({'results': results})


@csrf_exempt
def api_driver_location(request):
    """تحديث الموقع الحالي وأخذ عينة من المسار كل دقيقتين"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)

    if request.user.role != 'driver':
        return JsonResponse({'status': 'error', 'message': 'Driver account required'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    try:
        latitude = Decimal(str(data['latitude']))
        longitude = Decimal(str(data['longitude']))
        accuracy_value = data.get('accuracy')
        accuracy = float(accuracy_value) if accuracy_value is not None else None
    except (KeyError, TypeError, ValueError, InvalidOperation):
        return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)

    if (
        not latitude.is_finite()
        or not longitude.is_finite()
        or not Decimal('-90') <= latitude <= Decimal('90')
        or not Decimal('-180') <= longitude <= Decimal('180')
        or (accuracy is not None and (not math.isfinite(accuracy) or accuracy < 0))
    ):
        return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)

    now = timezone.now()
    current_location = DriverCurrentLocation.objects.filter(driver=request.user).first()
    if current_location and now - current_location.updated_at < timedelta(seconds=10):
        return JsonResponse({'status': 'error', 'message': 'Location update too frequent'}, status=429)

    DriverCurrentLocation.objects.update_or_create(
        driver=request.user,
        defaults={
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
        },
    )

    latest_route_point = request.user.locations.first()
    history_saved = False
    sample_due = (
        latest_route_point is None
        or now - latest_route_point.timestamp >= timedelta(minutes=2)
    )
    accurate_enough = accuracy is not None and accuracy <= 100
    if accurate_enough and sample_due:
        DriverLocation.objects.create(
            driver=request.user,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
        )
        history_saved = True
    
    return JsonResponse({'status': 'success', 'history_saved': history_saved})


@login_required
@user_passes_test(is_admin)
def api_driver_locations(request):
    """API للحصول على مواقع جميع المناديب"""
    drivers = User.objects.filter(role='driver').select_related('current_location')
    drivers_data = []
    
    for driver in drivers:
        locations = list(
            driver.locations.filter(accuracy__lte=100).order_by('-timestamp')[:50]
        )
        locations.reverse()
        current_location = getattr(driver, 'current_location', None)
        location_is_live = bool(
            current_location
            and timezone.now() - current_location.updated_at <= timedelta(minutes=1)
        )
        latest_location = current_location if location_is_live else None
        if latest_location is None and locations:
            latest_location = locations[-1]
        
        driver_info = {
            'id': driver.id,
            'username': driver.username,
            'latest_location': None,
            'locations': [],
            'location_is_live': location_is_live,
        }
        
        if latest_location:
            driver_info['latest_location'] = {
                'latitude': float(latest_location.latitude),
                'longitude': float(latest_location.longitude),
                'accuracy_m': latest_location.accuracy,
                'timestamp': (
                    latest_location.updated_at.isoformat()
                    if isinstance(latest_location, DriverCurrentLocation)
                    else latest_location.timestamp.isoformat()
                )
            }
        
        if locations:
            driver_info['locations'] = [
                {
                    'latitude': float(loc.latitude),
                    'longitude': float(loc.longitude),
                    'timestamp': loc.timestamp.isoformat()
                }
                for loc in locations
            ]
        
        drivers_data.append(driver_info)
    
    return JsonResponse({'drivers': drivers_data})
