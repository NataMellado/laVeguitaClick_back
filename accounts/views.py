from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import CustomUser
import json

# Create your views here.

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', None)
        usuario = data.get('usuario', None)
        password = data.get('password', None)

        if email is None or password is None or usuario is None:
            return JsonResponse({'error': 'Por favor ingrese email, password y usuario'},
                                status=400,
                                json_dumps_params={'ensure_ascii': False
                                                   })

        if email == '' or password == '' or usuario == '':
            return JsonResponse({'error': 'Por favor ingrese email, password y usuario'},
                                status=400,
                                json_dumps_params={'ensure_ascii': False
                                                   })

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'El email ya está en uso!'},
                                status=400,
                                json_dumps_params={'ensure_ascii': False
                                                   })

        user = CustomUser.objects.create_user(email=email, password=password, usuario=usuario, rol='gerente')
        user.save()
        return JsonResponse({'message': 'Usuario creado exitosamente!'},
                            status=201,
                            json_dumps_params={'ensure_ascii': False
                                               })
    return JsonResponse({'error': 'Petición inválida!'},
                        status=400,
                        json_dumps_params={'ensure_ascii': False
                                           })

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)

        usuario = authenticate(email=email, password=password)

        if usuario is not None:
            login(request, usuario)
            print("login exitoso")
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
# @login_required  # Solo usuarios autenticados pueden acceder a esta vista
def session_view(request):
    if request.user.is_authenticated:
        usuario = request.user
        return JsonResponse({
            'estaAutenticado': True,
            'usuario': usuario.usuario,
            'email': usuario.email,
            'rol': usuario.rol
        },
            json_dumps_params={'ensure_ascii': False
                               })
    else:
        print("no está autenticado")
        return JsonResponse({'estaAutenticado': False}, status=200)
