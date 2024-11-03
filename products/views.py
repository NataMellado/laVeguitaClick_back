from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, Category
from django.views.decorators.csrf import csrf_exempt
import json

# Products view
def products(request):
    products = Product.objects.all().select_related('category')
    products_data = []
    
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'stock': product.stock,
            'category': product.category.name,
            'image': product.image.url if product.image else None,
            'is_featured': product.is_featured
        })
    
    return JsonResponse({'products': products_data})

# Add product
@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        price = data.get('price')
        description = data.get('description')
        stock = data.get('stock')
        category_name = data.get('category')
        image = data.get('image', None)
        is_featured = data.get('is_featured', False)
        
        category = Category.objects.filter(name=category_name).first()

        product = Product.objects.create(
            name=name,
            price=price,
            description=description,
            stock=stock,
            category=category,
            image=image,
            is_featured=is_featured
        )

        return JsonResponse({'message': 'Producto creado correctamente'})
