from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('<int:pk>/assign-driver/', views.order_assign_driver, name='order_assign_driver'),
    path('<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('<int:pk>/print/', views.order_print, name='order_print'),
]
