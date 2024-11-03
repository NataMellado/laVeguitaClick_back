from django.shortcuts import render
from django.http import JsonResponse
from .models import Product, Category
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

# GET y POST para la lista de productos
@csrf_exempt
@require_http_methods(["GET", "POST"])
def products(request):
    if request.method == 'GET':
        products = Product.objects.all().select_related('category')
        products_data = [
            {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'stock': product.stock,
                'category': product.category.name,
                'image': product.image.url if product.image else None,
                'is_featured': product.is_featured
            }
            for product in products
        ]
        return JsonResponse({'products': products_data})
    
    elif request.method == 'POST':
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

# GET, PUT y DELETE para un producto específico
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

    if request.method == 'GET':
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'stock': product.stock,
            'category': product.category.name,
            'image': product.image.url if product.image else None,
            'is_featured': product.is_featured
        }
        return JsonResponse({'product': product_data})

    elif request.method == 'PUT':
        data = json.loads(request.body)
        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.description = data.get('description', product.description)
        product.stock = data.get('stock', product.stock)
        product.is_featured = data.get('is_featured', product.is_featured)

        category_name = data.get('category')
        if category_name:
            category = Category.objects.filter(name=category_name).first()
            product.category = category

        product.save()
        return JsonResponse({'message': 'Producto actualizado correctamente'})

    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse({'message': 'Producto eliminado correctamente'})
