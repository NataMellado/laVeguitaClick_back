from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, Category

# Products view
def products(request):
    products = Product.objects.all()
    products_data = list(products.values('id', 'name', 'price', 'description', 'stock', 'category__name', 'image', 'is_featured'))
    
    return JsonResponse({'products': products_data})
