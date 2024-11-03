from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

# Create your views here.


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)

        usuario = authenticate(email=email, password=password)

        if usuario is not None:
            login(request, usuario)
            return JsonResponse({'message': 'Login exitoso!', 'rol': usuario.rol},
                                status=200,
                                json_dumps_params={'ensure_ascii': False
                                                   })
        else:
            return JsonResponse({'error': 'Credenciales inválidas!'},
                                status=400,
                                json_dumps_params={'ensure_ascii': False
                                                   })
    return JsonResponse({'error': 'Petición inválida!'},
                        status=400,
                        json_dumps_params={'ensure_ascii': False
                                           })


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout exitoso!'},
                            status=200,
                            json_dumps_params={'ensure_ascii': False
                                               })
    return JsonResponse({'error': 'Petición inválida!'},
                        status=400,
                        json_dumps_params={'ensure_ascii': False
                                           })


@csrf_exempt
@login_required  # Solo usuarios autenticados pueden acceder a esta vista
def session_view(request):
    usuario = request.user
    if usuario is None:
        return JsonResponse({'estaAutenticado': False})
    return JsonResponse({
        'estaAutenticado': True,
        'usuario': usuario.username,
        'rol': usuario.rol
    },
        json_dumps_params={'ensure_ascii': False
                           })
