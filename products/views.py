from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, Category, Supplier
from django.views.decorators.http import require_http_methods 
from django.views.decorators.csrf import csrf_exempt
import json



# Función para serializar la instancia de un producto
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
    



# GET y POST para la lista de productos
@csrf_exempt
@require_http_methods(["GET", "POST"])
def products(request):
    
    # GET para obtener todos los productos
    if request.method == 'GET':
        products = Product.objects.select_related('category').all()
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
                return JsonResponse({'error': 'Por favor ingrese todos los campos requeridos'}, status=400)
        
            category = Category.objects.filter(name=category_name).first()
            if not category:
                return JsonResponse({'error': 'La categoría no existe'}, status=400)
        
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
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Los datos enviados no son válidos'}, status=400)




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
            return JsonResponse({'message': 'Producto actualizado correctamente'})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Los datos enviados no son válidos'}, status=400)
        
    # DELETE para eliminar un producto
    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse({'message': 'Producto eliminado correctamente'})




# GET y POST para la lista de proveedores
@csrf_exempt
@require_http_methods(["GET", "POST"])
def suppliers(request):
        
        # GET para obtener todos los proveedores
        if request.method == 'GET':
            suppliers = Supplier.objects.all()
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
                    return JsonResponse({'error': 'Por favor ingrese todos los campos requeridos'}, status=400)
            
                supplier = Supplier.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                return JsonResponse({'message': 'Proveedor creado correctamente'})
            
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Los datos enviados no son válidos'}, status=400)
            
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
            return JsonResponse({'message': 'Proveedor actualizado correctamente'})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Los datos enviados no son válidos'}, status=400)
        
    # DELETE para eliminar un proveedor
    elif request.method == 'DELETE':
        supplier.delete()
        return JsonResponse({'message': 'Proveedor eliminado correctamente'})
    
    
    
