from django.urls import path
from . import views

urlpatterns = [
    path('api/products/', views.products, name='products'),
    path('api/add-product/', views.add_product, name='add_product'),
]
