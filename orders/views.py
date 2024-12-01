from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Driver, Order, OrderItem, Vehicle, Product
from django.contrib.auth import get_user_model
import json

# Serializadores
def serialize_order(order):
    return {
        'id': order.id,
        'user': order.user.email,
        'status': order.status,
        'total_price': float(order.total_price),
        'vehicle': serialize_vehicle(order.vehicle) if order.vehicle else None,   
        'created_at': order.created_at.date().isoformat(),
        'updated_at': order.updated_at.date().isoformat(),
        'items': [serialize_order_item(item) for item in order.items.all()],
    }

def serialize_order_item(order_item):
    return {
        'id': order_item.id,
        'product': order_item.product.name,
        'quantity': order_item.quantity,
        'price': float(order_item.price),
        'total_price': float(order_item.get_total_price()),
    }

def serialize_vehicle(vehicle):
    return {
        'id': vehicle.id,
        'license_plate': vehicle.license_plate,
        'vehicle_type': vehicle.vehicle_type,
        'model': vehicle.model,
        'driver': serialize_driver(vehicle.driver) if vehicle.driver else None,
    }
    
def serialize_driver(driver):
    return {
        'id': driver.id,
        'user': { 
            'email': driver.user.email,
            'first_name': driver.user.first_name,
            'last_name': driver.user.last_name,
            },
        'phone_number': driver.phone_number,
        'license_number': driver.license_number,
    }


# GET y POST para la lista de órdenes
@csrf_exempt
@require_http_methods(["GET", "POST"])
def orders(request):
    User = get_user_model()

    if request.method == 'GET':
        # Ordenar según estado y fecha de creación
        orders = Order.objects.select_related('user').prefetch_related('items__product').all().order_by('-status', '-created_at')
        # orders = Order.objects.select_related('user').prefetch_related('items__product').all().order_by('-id')
        return JsonResponse({'orders': [serialize_order(order) for order in orders]})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_email = data.get('user_email')
            items_data = data.get('items', [])
            vehicle_id = data.get('vehicle_id')
            
            # Validar si el email fue proporcionado
            if not user_email:
                return JsonResponse({'status': 'error', 'message': 'El correo electrónico del usuario es obligatorio'}, status=400)

            # Buscar al usuario por email
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'El usuario con este correo no existe'}, status=400)

            # Validar que se proporcionen ítems
            if not items_data:
                return JsonResponse({'status': 'error', 'message': 'No se proporcionaron ítems'}, status=400)
            
            # Validar el vehículo si fue proporcionado
            vehicle = None
            if vehicle_id:
                try:
                    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
                except Vehicle.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'El vehículo no existe'}, status=400)
            

            # Crear la orden
            order = Order.objects.create(user=user, vehicle=vehicle)
            for item_data in items_data:
                product = get_object_or_404(Product, id=item_data['product_id'])
                if product.stock < item_data['quantity']:
                    return JsonResponse({'status': 'error', 'message': f'Stock insuficiente para {product.name}'}, status=400)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=product.price
                )
                product.stock -= item_data['quantity']
                product.save()

            order.calculate_total_price()
            return JsonResponse({'status': 'success', 'message':'Venta creada correctamente.'  ,'data': serialize_order(order)})

        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)

# GET, PUT y DELETE para una orden específica
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # GET para obtener una orden específica
    if request.method == 'GET':
        return JsonResponse({'order': serialize_order(order)})

    # PUT para actualizar una orden
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            order.status = data.get('status', order.status)            
            vehicle_id = data.get('vehicle')

            if vehicle_id is None or vehicle_id == "null":
                order.vehicle = None
            else:
                vehicle = get_object_or_404(Vehicle, id=vehicle_id)
                order.vehicle = vehicle
            
            order.save()
            return JsonResponse({
                'status': 'success', 
                'message': 'Venta actualizada correctamente',
                'order': serialize_order(order)
            }, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error', 
                'message': 'Datos inválidos'
            }, status=400)

    if request.method == 'DELETE':
        order.delete()
        return JsonResponse({'status': 'success', 'message': 'Venta eliminada correctamente'})

# GET y POST para los ítems de una orden
@csrf_exempt
@require_http_methods(["GET", "POST"])
def order_items(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'GET':
        items = [serialize_order_item(item) for item in order.items.all()]
        return JsonResponse({'status': 'success', 'data': items})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = get_object_or_404(Product, id=data['product_id'])
            if product.stock < data['quantity']:
                return JsonResponse({'status': 'error', 'message': f'Stock insuficiente para {product.name}'}, status=400)

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=data['quantity'],
                price=product.price
            )
            product.stock -= data['quantity']
            product.save()
            order.calculate_total_price()

            return JsonResponse({'status': 'success', 'data': serialize_order_item(order_item)})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)


# GET y POST para los vehículos
@csrf_exempt
@require_http_methods(["GET", "POST"])
def vehicles(request):

    if request.method == 'GET':
        # Ordenar por id de creación
        vehicles = Vehicle.objects.all().order_by('-id')
        return JsonResponse({'vehicles': [serialize_vehicle(vehicle) for vehicle in vehicles]})
    
    elif request.method == 'POST':
        
        try:
            data = json.loads(request.body)
            license_plate = data.get('license_plate')
            vehicle_type = data.get('vehicle_type')
            model = data.get('model')
            
            # Validar que la patente no esté en uso
            if Vehicle.objects.filter(license_plate=license_plate).exists():
                return JsonResponse({'status': 'error', 'message': 'La patente ya está en uso'}, status=400)
            
            # Crear el vehículo
            vehicle = Vehicle.objects.create(license_plate=license_plate, vehicle_type=vehicle_type, model=model)
            return JsonResponse({
                'status': 'success', 
                'message':'Vehículo creado correctamente.',
                'data': serialize_vehicle(vehicle)})

        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)
    
# GET, PUT y DELETE para un vehículo específico
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id) 
    
    # GET para obtener un vehículo específico
    if request.method == 'GET':
        return JsonResponse({'vehicle': serialize_vehicle(vehicle)})

    # PUT para actualizar un vehículo
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)   
            new_license_plate = data.get('license_plate', vehicle.license_plate)
            
            if Vehicle.objects.filter(license_plate=new_license_plate).exclude(id=vehicle.id).exists():
                return JsonResponse({'status': 'error', 'message': 'La patente ya está en uso'}, status=400)
            
            driver_id = data.get('driver')

            if driver_id is None or driver_id == "null":
                vehicle.driver = None
            else:
                driver = get_object_or_404(Driver, id=driver_id)
                vehicle.driver = driver
                
            vehicle.license_plate = new_license_plate
            vehicle.vehicle_type = data.get('vehicle_type', vehicle.vehicle_type)
            vehicle.model = data.get('model', vehicle.model)    
            
            vehicle.save()
            return JsonResponse({
                'status': 'success', 
                'message': 'Vehículo actualizado correctamente',
                'vehicle': serialize_vehicle(vehicle)
            }, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error', 
                'message': 'Datos inválidos'
            }, status=400)

    if request.method == 'DELETE':
        vehicle.delete()
        return JsonResponse({'status': 'success', 'message': 'Vehículo eliminado correctamente'})
    

# GET y POST para los conductores
@csrf_exempt
@require_http_methods(["GET", "POST"])
def drivers(request):

    if request.method == 'GET':
        drivers = Driver.objects.all().order_by('id')
        return JsonResponse({'drivers': [serialize_driver(driver) for driver in drivers]})

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            license_number = data.get('license_number')
            user_email = data.get('user_email')
            
            User = get_user_model()
            user = User.objects.filter(email=user_email).first()
            
            if not user:
                return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, status=400)
            
            if Driver.objects.filter(user=user).exists():
                return JsonResponse({'status': 'error', 'message': 'El usuario ya tiene un conductor asociado'}, status=400)
            
            # Crear el conductor
            driver = Driver.objects.create(phone_number=phone_number, license_number=license_number, user=user)
            return JsonResponse({
                'status': 'success', 
                'message':'Conductor creado correctamente.',
                'data': serialize_driver(driver)})

        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)
    

# GET, PUT y DELETE para un conductor específico
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def driver_detail(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id) 
    
    # GET para obtener un conductor específico
    if request.method == 'GET':
        return JsonResponse({'driver': serialize_driver(driver)})

   # PUT para actualizar un conductor
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)    
            new_license_number = data.get('license_number', driver.license_number) 
            if Driver.objects.filter(license_number=new_license_number).exclude(id=driver.id).exists():
                return JsonResponse({'status': 'error', 'message': 'La licencia ya está en uso'}, status=400)
            
            driver.phone_number = data.get('phone_number', driver.phone_number)
            driver.license_number = new_license_number
    
            driver.save() 
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Conductor actualizado correctamente',
                'driver': serialize_driver(driver)
            }, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error', 
                'message': 'Datos inválidos'
            }, status=400)

    if request.method == 'DELETE':
        
        driver.delete()
        return JsonResponse({'status': 'success', 'message': 'Conductor eliminado correctamente'})
    
