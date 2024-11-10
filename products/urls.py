from django.urls import path
from . import views

urlpatterns = [
    path('api/products/', views.products, name='products'),
    path('api/products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/products/add/', views.products, name='add_product'),
    path('api/suppliers/', views.suppliers, name='suppliers'),
    path('api/suppliers/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
]
