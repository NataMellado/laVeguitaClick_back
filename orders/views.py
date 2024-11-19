from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, Vehicle, Product
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
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
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
        'driver': serialize_driver(vehicle.driver) if vehicle.driver else None,
    }
    
def serialize_driver(driver):
    return {
        'id': driver.id,
        'user': driver.user.email,
        'phone_number': driver.phone_number,
        'license_number': driver.license_number,
    }


# GET y POST para la lista de órdenes
@csrf_exempt
@require_http_methods(["GET", "POST"])
def orders(request):
    User = get_user_model()

    if request.method == 'GET':
        orders = Order.objects.select_related('user').prefetch_related('items__product').all().order_by('-id')
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


# GET para la lista de vehículos
@csrf_exempt
@require_http_methods(["GET"])
def vehicles(request):
    
    
    if request.method == 'GET':
        vehicles = Vehicle.objects.all()
        vehicles_data = [serialize_vehicle(vehicle) for vehicle in vehicles]
        return JsonResponse({'vehicles': vehicles_data})
