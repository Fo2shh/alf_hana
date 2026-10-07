from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('menu/', views.menu_management, name='menu_management'),
    path('menu/categories/', views.category_list, name='category_list'),
    path('menu/categories/add/', views.category_add, name='category_add'),
    path('menu/categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('menu/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('menu/items/add/', views.menu_item_add, name='menu_item_add'),
    path('menu/items/<int:pk>/edit/', views.menu_item_edit, name='menu_item_edit'),
    path('menu/items/<int:pk>/delete/', views.menu_item_delete, name='menu_item_delete'),
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('drivers/', views.drivers_list, name='drivers_list'),
    path('drivers/map/', views.drivers_map, name='drivers_map'),
    path('driver-app/', views.driver_app, name='driver_app'),
    path('api/customer-search/', views.api_customer_search, name='api_customer_search'),
    path('api/menu-search/', views.api_menu_search, name='api_menu_search'),
    path('api/driver-location/', views.api_driver_location, name='api_driver_location'),
    path('api/driver-locations/', views.api_driver_locations, name='api_driver_locations'),
]
