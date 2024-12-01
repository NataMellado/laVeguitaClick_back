from django.urls import path
from . import views

urlpatterns = [
    path('api/orders/', views.orders, name='orders'), 
    path('api/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('api/orders/<int:order_id>/items/', views.order_items, name='order_items'),  
    path('api/vehicles/', views.vehicles, name='vehicles'),
    path('api/vehicles/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('api/drivers/', views.drivers, name='drivers'),
    path('api/drivers/<int:driver_id>/', views.driver_detail, name='driver_detail'),
]
