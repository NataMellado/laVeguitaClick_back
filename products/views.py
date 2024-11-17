from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, Category, Supplier
from django.views.decorators.http import require_http_methods 
from django.views.decorators.csrf import csrf_exempt
import json



# Función para serializar la instancia de un producto, osea, convertirlo en un diccionario de Python 
# para que pueda ser convertido a JSON
def serialize_product(product):
    return {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'description': product.description,
        'stock': product.stock,
        'category': product.category.name,
        'image': product.image.url if product.image else None,
        'is_featured': product.is_featured
    }
    
# Función para serializar la instancia de un proveedor
def serialize_supplier(supplier):
    return {
        'id': supplier.id,
        'name': supplier.name,
        'email': supplier.email,
        'phone': supplier.phone,
        'address': supplier.address
    }
    
# Funciòn para serializar la instancia de una categoría
def serialize_category(category):
    return {
        'id': category.id,
        'name': category.name
    }
    
# GET y POST para la lista de categorías
@csrf_exempt
@require_http_methods(["GET", "POST"])
def categories(request):
    
    # GET para obtener todas las categorías en orden de creación
    if request.method == 'GET':
        categories = Category.objects.all().order_by('-id')
        categories_data = [serialize_category(category) for category in categories]
        return JsonResponse({'categories': categories_data})
    
    # POST para añadir una nueva categoría
    elif request.method == 'POST':
        
        try: 
            data = json.loads(request.body)
            name = data.get('name')
            
            if not name:
                return JsonResponse({
                    'status': 'alert',
                    'message': 'Por favor ingrese el nombre de la categoría'
                }, status=400)
        
            category = Category.objects.create(name=name)
            return JsonResponse({
                'status': 'success',
                'message': 'Categoría creada correctamente'
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Los datos enviados no son válidos'
            }, status=400)

# GET, PUT y DELETE para una categoría específica
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # GET para obtener una categoría específica
    if request.method == 'GET':
        return JsonResponse({'category': serialize_category(category)})

    # PUT para actualizar una categoría
    elif request.method == 'PUT':
        try: 
            data = json.loads(request.body)
            category.name = data.get('name', category.name)
            category.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Categoría actualizada correctamente'
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Los datos enviados no son válidos'
            }, status=400)
        
    # DELETE para eliminar una categoría
    elif request.method == 'DELETE':
        if Product.objects.filter(category=category).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'No se puede eliminar la categoría porque tiene productos asociados'
            }, status=400)
            
        category.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Categoría eliminada correctamente'
        }, status=200)

# GET y POST para la lista de productos
@csrf_exempt
@require_http_methods(["GET", "POST"])
def products(request):
    
    # GET para obtener todos los productos en orden de creación
    if request.method == 'GET':
        products = Product.objects.select_related('category').all().order_by('-id')
        products_data = [serialize_product(product) for product in products]
        return JsonResponse({'products': products_data})
    
    # POST para añadir un nuevo producto
    elif request.method == 'POST':
        
        try: 
            data = json.loads(request.body)
            name = data.get('name')
            price = data.get('price')
            description = data.get('description')
            stock = data.get('stock')
            category_name = data.get('category')
            image = data.get('image', None)
            is_featured = data.get('is_featured', False)
            
            if not all([name, price, description, stock, category_name]):
                return JsonResponse({
                    'status': 'alert',
                    'message': 'Por favor ingrese todos los campos requeridos'
                }, status=400)
        
            category = Category.objects.filter(name=category_name).first()
            if not category:
                return JsonResponse({
                    'status': 'error',
                    'message': 'La categoría no existe'
                }, status=400)
        
            product = Product.objects.create(
                name=name,
                price=price,
                description=description,
                stock=stock,
                category=category,
                image=image,
                is_featured=is_featured
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Producto creado correctamente'
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Los datos enviados no son válidos'
            }, status=400)

# GET, PUT y DELETE para un producto específico
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # GET para obtener un producto específico
    if request.method == 'GET':
        return JsonResponse({'product': serialize_product(product)})

    # PUT para actualizar un producto
    elif request.method == 'PUT':
        try: 
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
            return JsonResponse({
                'status': 'success',
                'message': 'Producto actualizado correctamente'
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Los datos enviados no son válidos'
            }, status=400)
        
    # DELETE para eliminar un producto
    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Producto eliminado correctamente'
        }, status=200)

# GET y POST para la lista de proveedores
@csrf_exempt
@require_http_methods(["GET", "POST"])
def suppliers(request):
        
        # GET para obtener todos los proveedores en orden de creación
        if request.method == 'GET':
            suppliers = Supplier.objects.all().order_by('-id')
            suppliers_data = [serialize_supplier(supplier) for supplier in suppliers]
            return JsonResponse({'suppliers': suppliers_data})
        
        # POST para añadir un nuevo proveedor
        elif request.method == 'POST':
            
            try: 
                data = json.loads(request.body)
                name = data.get('name')
                email = data.get('email')
                phone = data.get('phone')
                address = data.get('address')
                
                if not all([name, email, phone, address]):
                    return JsonResponse({
                        'status': 'alert',
                        'message': 'Por favor ingrese todos los campos requeridos'
                    }, status=400)
            
                supplier = Supplier.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                return JsonResponse({
                    'status': 'success',
                    'message': 'Proveedor creado correctamente'
                })
            
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Los datos enviados no son válidos'
                }, status=400)
            
# GET, PUT y DELETE para un proveedor específico
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    # GET para obtener un proveedor específico
    if request.method == 'GET':
        return JsonResponse({'supplier': serialize_supplier(supplier)})

    # PUT para actualizar un proveedor
    elif request.method == 'PUT':
        try: 
            data = json.loads(request.body)
            supplier.name = data.get('name', supplier.name)
            supplier.email = data.get('email', supplier.email)
            supplier.phone = data.get('phone', supplier.phone)
            supplier.address = data.get('address', supplier.address)
            supplier.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Proveedor actualizado correctamente'
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Los datos enviados no son válidos'
            }, status=400)
        
    # DELETE para eliminar un proveedor
    elif request.method == 'DELETE':
        supplier.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Proveedor eliminado correctamente'
        }, status=200)
                        
    
    
    
